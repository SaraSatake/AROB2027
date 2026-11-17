import mesa
import random
import numpy as np
from pathlib import Path
from .plant_agent import PlantAgent
from .hominid_agent import HominidAgent, NestAgent
from .carcass_agent import CarcassAgent
from .hyena_agent import HyenaAgent
from .crocodile_agent import CrocodileAgent
from mesa.datacollection import DataCollector
import csv
import pandas as pd
import math
import matplotlib.pyplot as plt


from .scheduler import RandomActivationByTypeFiltered

external_file = "tables.txt"



class CustomMultiGrid(mesa.space.MultiGrid):
    def __init__(self, width, height, torus):
        super().__init__(width, height, torus)
        self.coord_attributes = {}  # Custom attribute dictionary for coordinates

    def add_coord_attribute(self, coord, attribute_value):
        """
        Add a custom attribute to a specific coordinate.

        Args:
            coord: The coordinate tuple (x, y) to which the attribute should be added.
            attribute_name: The name of the custom attribute.
            attribute_value: The value of the custom attribute.
        """
        coord_tuple = tuple(coord)  # Convert the list to a tuple

        if coord_tuple not in self.coord_attributes:
            self.coord_attributes[coord_tuple] = {}
        self.coord_attributes[coord_tuple] = attribute_value

    def get_coord_attribute(self, coord):
        """
        Get the value of a custom attribute for a specific coordinate.

        Args:
            coord: The coordinate tuple (x, y) for which to retrieve the attribute.
            attribute_name: The name of the custom attribute.

        Returns:
            The value of the custom attribute for the coordinate.
        """
        coord_tuple = tuple(coord)  # Convert the list to a tuple

        if coord_tuple in self.coord_attributes:
            return self.coord_attributes[coord_tuple]
        else:
            return None


class HominidsModel(mesa.Model):
    """Replicates the HOMINIDS paper"""

    def __init__(self, width, height, path=None, number_hominids_followers=0, number_hominids_explorers = 0, number_plantsA=0, number_plantsB=0, number_plantsC=0, number_plantsD=0,number_nests=0, number_hyenas=0, number_crocodiles=0):
        super().__init__()


        # Model parameters. TODO: make it read from passed dictionary
        self.number_hominids_followers = number_hominids_followers
        self.number_hominids_explorers = number_hominids_explorers
        self.number_plantsA = number_plantsA
        self.number_plantsB = number_plantsB
        self.number_plantsC = number_plantsC
        self.number_plantsD = number_plantsD
        self.number_nests = number_nests
        self.number_hyenas = number_hyenas
        self.number_crocodiles = number_crocodiles
        self.max_attr_history = []
        self.max_rep_history = []
        self.carcass_probability = {'Channel': 0.0004566210, 'Flooded': 0.0001948250, 'Unflooded': 0.0002739726, 'Plant': 0, 'Hominid': 0, 'Nest': 0} # Probabilities by cell types according to the paper
        
        # model variables
        self.time = 0
        self.DAY_LENGTH = 720 # (1 step per minute)

        self.hominid_best_fed = None
        self.minumum_hominids = 10
        self.list_hominids = []
        self.detection_range = math.ceil((((width*height)*5)/100) / 8)
        #print("detenction range: ", self.detection_range)
        
        self.sum_total_calories_per_day = []
        self.calories_per_day = []
        self.calories_per_day_after_sharing = []
        self.sum_total_calories_per_day_after_sharing = []
        self.last_nest_id = None
        #self.possible_nests = []
        self.random_cell_choice = None
        self.calories_explorers_per_day = []
        self.calories_followers_per_day = []

        self.calories_aftersharing_explorers_per_day = []
        self.calories_aftersharing_followers_per_day = []


        # Try reading csv file from the path:
        try:
            grid_data = np.genfromtxt(path, delimiter=',')
            grid_data = np.transpose(grid_data)
            print("Generating grid according to csv data")
            # change grid size parameters according to csv data
            width = grid_data.shape[0]
            height = grid_data.shape[1]

        except Exception as e:
            print(f"Warning: Failed to read the CSV file. Proceding with random celltype generation. Error: {e}")
            grid_data = np.random.choice([0, 1, 2], size=(width, height))
        
        # Last parameter is toroidal
        self.grid = CustomMultiGrid(width, height, False)
        self.gridVisualization = CustomMultiGrid(width, height, False)
        self.gridHeatMap = CustomMultiGrid(width, height, False)
        self.gridHeatMapExplorers = CustomMultiGrid(width, height, False)
        self.gridHeatMapFollowers = CustomMultiGrid(width, height, False)
        self.gridPheromone = CustomMultiGrid(width, height, False)
        self.gridDangerousPheromone = CustomMultiGrid(width, height, False)
        self.gridCalculusPheromone = CustomMultiGrid(width, height, False)
        
        # Randomly assign type to cells

        cell_types = {0:'Channel', 1:'Flooded', 2:'Unflooded'}

        for coord in self.grid.coord_iter():
            grid_data_value = grid_data[coord[1]]
            self.grid.add_coord_attribute(coord[1], cell_types[grid_data_value])
            self.gridVisualization.add_coord_attribute(coord[1], cell_types[grid_data_value])
            self.gridHeatMap.add_coord_attribute(coord[1], "0")
            self.gridHeatMapExplorers.add_coord_attribute(coord[1], "0")
            self.gridHeatMapFollowers.add_coord_attribute(coord[1], "0")
            self.gridPheromone.add_coord_attribute(coord[1], "0")
            self.gridDangerousPheromone.add_coord_attribute(coord[1], "0")
            self.gridCalculusPheromone.add_coord_attribute(coord[1], "0")
        

        

        
        # for coord in self.grid.coord_iter():
        #     random_type = self.random.choice(list(cell_types.values()))
        #     self.grid.add_coord_attribute(coord[1], random_type)

        # Creating schedulers
        self.schedule = RandomActivationByTypeFiltered(self)

        self.running = True # enables conditional shutdown of the model when batch running

        # Creating Agents
       
        ## Creating Plants() - ID, self, type, fruit weight, fruit calories, K (maximum carry capacity), r (growth rate)

        while True:

            numberOfPlantClusters = self.random.randint(3, 8)
            #print("Number of plant clusters: ", numberOfPlantClusters)
            listPlantClusterOrigins = []
            
            while numberOfPlantClusters != len(listPlantClusterOrigins):
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)

                if self.grid.get_coord_attribute((x,y)) != 'Channel':

                    PlantClusterOrigin = (x,y)
                    listPlantClusterOrigins.append(PlantClusterOrigin)

            #print("Cluster origins: ",listPlantClusterOrigins)
            listPlantClustersCoordinates = []

            for plantOrigin in listPlantClusterOrigins:        
                neighbor = self.grid.get_neighborhood(
                plantOrigin,
                moore=True,  # Consider 8 neighbors
                include_center=True,
                radius=15
                )
                listPlantClustersCoordinates.append(neighbor)
            
            contChannel = 0
            contFlooded = 0
            contUnflooded = 0

            for cluster in listPlantClustersCoordinates:
                for coord in cluster:
                    terrain = self.grid.get_coord_attribute(coord)

                    if terrain == 'Channel':
                        contChannel += 1
                    elif terrain == 'Flooded':
                        contFlooded += 1
                    elif terrain == 'Unflooded':
                        contUnflooded += 1

            if self.number_plantsA <= contFlooded and self.number_plantsB + self.number_plantsC + self.number_plantsD <= contUnflooded:
                break

        # print("Cont Channel: ", contChannel, "Cont Flooded: ", contFlooded, "Cont Unflooded: ", contUnflooded)
        # print("Possible neighbors: ",listPlantClustersCoordinates)    

        # Creating Plants type "A"
        gridPlants = np.zeros((width, height))
        for i in range(self.number_plantsA):
            a = PlantAgent(self.next_id(), self, "plantA", 5, 0.03, 15, 0.4, listPlantClustersCoordinates) 
            self.schedule.add(a)
            self.grid.place_agent(a, a.start_location)
            self.grid.add_coord_attribute(a.start_location, 'PlantA')
            #print("Plant A being located at", a.start_location, "at", grid_data[a.start_location] )
            self.gridVisualization.add_coord_attribute(a.start_location, 'PlantA')
            gridPlants[a.start_location[0]][a.start_location[1]] = 1 + gridPlants[a.start_location[0]][a.start_location[1]]
            #print("Plant - ID: ",a.unique_id, " being placed at", a.start_location)
        csv_plants= "PlantsMap.csv"
        
        # Creating Plants type "B"
        for i in range(self.number_plantsB):
            a = PlantAgent(self.next_id(), self, "plantB", 2, 0.1, 50, 0.2, listPlantClustersCoordinates)
            self.schedule.add(a)
            self.grid.place_agent(a, a.start_location)
            self.grid.add_coord_attribute(a.start_location, 'PlantB')
            #print("Plant B being located at", a.start_location, "at", grid_data[a.start_location] )
            self.gridVisualization.add_coord_attribute(a.start_location, 'PlantB')

            # Creating Plants type "C"
        for i in range(self.number_plantsC):
            a = PlantAgent(self.next_id(), self, "plantC", 20, 1, 200, 0.1, listPlantClustersCoordinates)
            self.schedule.add(a)
            self.grid.place_agent(a, a.start_location)
            self.grid.add_coord_attribute(a.start_location, 'PlantC')
            #print("Plant C being located at", a.start_location)
            self.gridVisualization.add_coord_attribute(a.start_location, 'PlantC')

            # Creating Plants type "D"
        for i in range(self.number_plantsD):
            a = PlantAgent(self.next_id(), self, "plantD", 10, 0.5, 30, 0.3, listPlantClustersCoordinates)
            self.schedule.add(a)
            self.grid.place_agent(a, a.start_location)
            self.grid.add_coord_attribute(a.start_location, 'PlantD')
            #print("Plant D being located at", a.start_location, " and has ", a.fruits)
            self.gridVisualization.add_coord_attribute(a.start_location, 'PlantD')

        # Escrever a matriz no arquivo CSV
        np.savetxt(csv_plants, gridPlants, delimiter=",")
       
        plant_map_csv= 'PlantsMap.csv'
        with open(plant_map_csv, 'r') as csvfile:
            reader_csv = csv.reader(csvfile)
            lines = list(reader_csv)
        list_nests = []
        ## Creating Nests
        for i in range(self.number_nests):
            a = NestAgent(self.next_id(), self)
            self.schedule.add(a)
            self.grid.place_agent(a, a.start_location)
            list_nests.append(a)
            self.grid.add_coord_attribute(a.start_location, 'Nest')
            self.gridVisualization.add_coord_attribute(a.start_location, 'Nest')
            # Put nests in PlantsMap.csv
            lines[a.start_location[0]][a.start_location[1]] = str('20')
            with open(plant_map_csv, 'w', newline='') as csvfile:
                writer_csv = csv.writer(csvfile)
                for linha in lines:
                    writer_csv.writerow(linha)
            
            #print("Nest - ID: ",a.unique_id, " being placed at", a.start_location)

        random_nest = random.choice(list_nests) # Choose a random nest to start

        
        ## Creating Hominids    
        for i in range(self.number_hominids_followers):
            a = HominidAgent(self.next_id(), self, "hominin_follower",random_nest)
            self.schedule.add(a)
            random_nest.add_hominid(a)
            self.grid.place_agent(a, random_nest.start_location)
            self.grid.add_coord_attribute(random_nest.start_location, 'Hominid')
            print("Hominin Follower created")
            self.gridVisualization.add_coord_attribute(random_nest.start_location, 'Hominid')
            self.list_hominids.append(a)

        for i in range(self.number_hominids_explorers):
            a = HominidAgent(self.next_id(), self, "hominin_explorer", random_nest)
            self.schedule.add(a)
            random_nest.add_hominid(a)
            self.grid.place_agent(a, random_nest.start_location)
            self.grid.add_coord_attribute(random_nest.start_location, 'Hominid')
            print("Hominin Explorer created")
            self.gridVisualization.add_coord_attribute(random_nest.start_location, 'Hominid')
            self.list_hominids.append(a)    

        self.hominid_datacollector = DataCollector(
           
            agent_reporters={"Caloric_need": "caloric_need"}
        )

        self.grid.add_coord_attribute(random_nest.start_location, 'Nest')

        self.nest_datacollector = DataCollector(
           
            agent_reporters={"Extra_Food_Cal": lambda agent: agent.extra_food_cal if isinstance(agent, NestAgent) else None}
        )
    
        
        ## Creating Animals
            #Creating hyena
        for i in range(self.number_hyenas):
            a = HyenaAgent(self.next_id(), self)
            self.schedule.add(a)
            self.grid.place_agent(a, a.start_location)
            #self.grid.add_coord_attribute(a.start_location, 'Animal')
            #self.gridVisualization.add_coord_attribute(a.start_location, 'Animal')

            #Creating crocodile
        for i in range(self.number_crocodiles):
            a = CrocodileAgent(self.next_id(), self)
            self.schedule.add(a)
            self.grid.place_agent(a, a.start_location)        

    def step(self):
        self.time += 1
        
        # Generate carcasses
        if self.time % self.DAY_LENGTH == 0:
            

            # for i in range(self.carcass_probability):
            #     a = CarcassAgent(self.next_id(), self)
            #     self.schedule.add(a)
            #     self.grid.place_agent(a, a.start_location)

            # Data collector
            self.hominid_datacollector.collect(self)
            self.nest_datacollector.collect(self)  

            

            
            caloric_needs = []
            underfed_hominids = []
            min_caloric_need = float('inf')
            hominid_with_min_caloric_need = None
            calories_consumed = 0
            total_calories_per_day = []
            total_calories_explorers_per_day = []
            total_calories_followers_per_day = []

            for agent in self.schedule.agents:
                if isinstance(agent, HominidAgent):
                    calories_consumed = agent.DAILY_CALORIC_NEED - agent.caloric_need
                    total_calories_per_day.append(calories_consumed)

                    if agent.hominin_type == "hominin_explorer":
                       total_calories_explorers_per_day.append(calories_consumed)
                    elif agent.hominin_type == "hominin_follower":
                        total_calories_followers_per_day.append(calories_consumed)     
            
            #print("Total calories consumed by each hominid: ",total_calories_per_day)
            sum_calories = sum(total_calories_per_day)
            self.sum_total_calories_per_day.append(sum_calories) #Stores all calories consumed in the day (each index represents a day)
            #print("Sum total calories per day: ",self.sum_total_calories_per_day)
            self.calories_per_day.append(total_calories_per_day) #For boxplot
            self.calories_explorers_per_day.append(total_calories_explorers_per_day)
            self.calories_followers_per_day.append(total_calories_followers_per_day)

            for agent in self.schedule.agents:
                if isinstance(agent, HominidAgent):
                    caloric_needs.append(agent.caloric_need)
                    if(agent.caloric_need > 0):
                        agent.nest.add_underfed_hominid_before_sharing_food(agent)
                        underfed_hominids.append(agent)

            for agent in self.schedule.agents:
                if isinstance(agent, HominidAgent):
                    caloric_need = agent.caloric_need
                    # Verificar se a necessidade calórica é menor do que a menor necessidade calórica encontrada até agora
                    if caloric_need < min_caloric_need:
                        min_caloric_need = caloric_need
                        self.hominid_best_fed = agent
                        



            #print("All caloric needs: ")
            # for a in caloric_needs:
            #     print(a)
            #print("Underfed hominid agents data:") 
            for a in underfed_hominids:
                print("Hominid ", a.unique_id, " is underfed and has ", a.caloric_need, " of caloric need and can receive until ",a.MAX_GUT_CAPACITY - a.gut, " grams of food in the gut.")

            
            #hominids_data = self.hominid_datacollector.get_agent_vars_dataframe()
            #hominids_starving = hominids_data[hominids_data['Caloric_need'] > 0]
              
    
            if self.hominid_best_fed:
                print("Hominid agent with the lowest caloric need (best-fed agent):", self.hominid_best_fed.unique_id, "with ",self.hominid_best_fed.caloric_need, " cal")
            else:
                print("Could not find a hominid agent with the lowest caloric need.")            
            # Printing all underfed homind agents
                
           

            # Calculating the total extra food (weight and cal)
            total_extra_food_cal = sum([nest.extra_food_cal for nest in self.schedule.agents if isinstance(nest, NestAgent)])
            total_extra_food_weight = sum([nest.extra_food_weight for nest in self.schedule.agents if isinstance(nest, NestAgent)])
            
            #print("Total of extra food: ", total_extra_food_weight,"grams and ", total_extra_food_cal, "cal")
            
            if len(underfed_hominids) > 0:
                ################ THIS PART IS FOR SHARING FOOD ####################
                list_received_food_hominids = []
                print("Share extra food with: ",len(underfed_hominids))
                self.share_food_equally(total_extra_food_cal, underfed_hominids) #Hominids receive extra food
                #print("Updated caloric needs after sharing food:")
                for hominid in underfed_hominids:
                    list_received_food_hominids.append(hominid)


                after_sharing_food = []
                for h in list_received_food_hominids:
                    #print(f"Hominídeo {h.unique_id}: Caloric need = {h.caloric_need}")
                    if(h.caloric_need > 0):
                        after_sharing_food.append(h)
                    else:
                        print("Hominid ",h.unique_id, " is full now")

                for a in after_sharing_food:
                    print("Hominid ",a.unique_id, "is still starving")

                #Verifying if there are enough underfed hominids
                #######################################################################
                if len(after_sharing_food) > self.minumum_hominids: ### WHEN SHARING FOOD, CHANGE "underfed_hominins" FOR "after_sharing_food"
                    print("There are enough underfed hominids, so nest is being realocated")
                    nearest_nest = self.find_nearest_nest()
                    
                    for h in self.list_hominids:
                        print("Moving nest to: ", nearest_nest.get_position())
                        self.gridVisualization.add_coord_attribute(h.pos, self.grid.get_coord_attribute(h.pos))
                        self.grid.move_agent(h, nearest_nest.get_position()) #If so, the best-fed hominid leads the group to the place where he last consumed food
                        self.gridVisualization.add_coord_attribute(h.nest.get_position(), 'Hominid')

                else:
                    print("Nest can stay in the same spot")
                    for h in self.list_hominids:
                        self.gridVisualization.add_coord_attribute(h.pos, self.grid.get_coord_attribute(h.pos))
                        self.grid.move_agent(h, h.nest.get_position()) #If not, the group returns to the current nest/
                        self.gridVisualization.add_coord_attribute(h.nest.get_position(), 'Hominid')
            
            else:
                print("There were not underfed hominids enough, so nest will not change")
                for h in self.list_hominids:
                    self.gridVisualization.add_coord_attribute(h.pos, self.grid.get_coord_attribute(h.pos))
                    self.grid.move_agent(h, h.nest.get_position())
                    self.gridVisualization.add_coord_attribute(h.nest.get_position(), 'Hominid')
            
            total_calories_per_day_after_sharing = []
            calories_consumed_after_sharing = 0
            total_calories_aftersharing_explorers_per_day = []
            total_calories_aftersharing_followers_per_day = []

            for agent in self.schedule.agents:
                if isinstance(agent, HominidAgent):
                    calories_consumed_after_sharing = agent.DAILY_CALORIC_NEED - agent.caloric_need
                    total_calories_per_day_after_sharing.append(calories_consumed_after_sharing)

                    if agent.hominin_type == "hominin_explorer":
                       total_calories_aftersharing_explorers_per_day.append(calories_consumed_after_sharing)
                    elif agent.hominin_type == "hominin_follower":
                        total_calories_aftersharing_followers_per_day.append(calories_consumed_after_sharing)

            self.calories_per_day_after_sharing.append(total_calories_per_day_after_sharing)
            sum_calories_after_sharing = sum(total_calories_per_day_after_sharing)
            self.sum_total_calories_per_day_after_sharing.append(sum_calories_after_sharing)
            self.calories_aftersharing_explorers_per_day.append(total_calories_aftersharing_explorers_per_day)
            self.calories_aftersharing_followers_per_day.append(total_calories_aftersharing_followers_per_day)
           
           #Zerar o extra food dos nests
            for agent in self.schedule.agents:
                if isinstance(agent, NestAgent):
                    agent.reset_extra_food()               
    
        # Step scheduler (agents)
        self.schedule.step()
        #print("oi estou no step ",self.time)
        self.max_attr = self.get_max_attractive_pheromone()
        self.max_rep = self.get_max_repulsive_pheromone()

        self.max_attr_history.append(self.max_attr)
        self.max_rep_history.append(self.max_rep)
    
    def get_max_attractive_pheromone(self):
        max_value = 0
        for index in self.gridPheromone.coord_iter():
            coord = index[1] #to get the coordenate
            value = float(self.gridPheromone.get_coord_attribute(coord))
            
            if value > max_value:
                max_value = value
        return max_value        

    def get_max_repulsive_pheromone(self):
        max_value = 0
        for index in self.gridDangerousPheromone.coord_iter():
            coord = index[1] #to get the coordenate
            value = float(self.gridDangerousPheromone.get_coord_attribute(coord))
            
            if value > max_value:
                max_value = value
        return max_value 

    

    def print_final_table(self):
    
        nests_data = self.nest_datacollector.get_agent_vars_dataframe()
        print("Nests data:")
        nests_extra_food = nests_data['Extra_Food_Cal']
        data_without_nan = nests_data.dropna(subset=['Extra_Food_Cal'])

        print("Extra food cal of all nests:")
        print(data_without_nan)
        data_string = data_without_nan.to_string()

       
        with open('extra_food_nests.txt', 'w') as file:
            file.write("Nests data:\n")
            file.write(data_string + "\n\n")

    def get_hominid_by_id(self, hominid_id):
        
        for agent in self.schedule.agents:
            if isinstance(agent, HominidAgent) and agent.unique_id == hominid_id:
                return agent
        return None  
    
    
    def find_nearest_nest(self):

        exploration_cell = self.hominid_best_fed.last_feed_place
        visit_order = ()
        visited_cells = []
       
        while True:
            possible_neighbors = self.grid.get_neighborhood(exploration_cell, moore = True, include_center = False, radius=10)    

            for elemento in possible_neighbors:
                if elemento in visited_cells:
                    possible_neighbors = tuple(x for x in possible_neighbors if x != elemento) 
            
            visit_order = visit_order + possible_neighbors
            
            for i in possible_neighbors:
                visited_cells.append(i)
            
            
            current_cell = visit_order[0]
            
            
            visit_order = tuple(x for x in visit_order if x != visit_order[0])


            cell_contents = self.grid.get_cell_list_contents([current_cell])
            
            for content in cell_contents:
                #print("tipo de celula: ", content.agent_type)
                
                if content.agent_type == "nest":

                    for hominid in self.list_hominids:
                        content.add_hominid(hominid)

                    return content
                
           
            exploration_cell = current_cell
    
    def share_food_equally(self, extra_food_cal, total_underfed_hominids):
        
        if len(total_underfed_hominids) == 0:
            return

        calories_per_hominid = (
            extra_food_cal / len(total_underfed_hominids)
        )

        for hominid in total_underfed_hominids:

            calories_received = min(
                calories_per_hominid,
                hominid.caloric_need
            )

            hominid.caloric_need -= calories_received

            print(
                "Hominid",
                hominid.unique_id,
                "received",
                round(calories_received, 2),
                "calories"
            )


    def share_food_priority(self, extra_food_weight, extra_food_cal, total_underfed_hominids):
        # Sort hominids by caloric need (from hungriest to least hungry)
        hominids_sorted = sorted(total_underfed_hominids, key=lambda x: x.caloric_need, reverse=True)
        print("Hominids sorted: ",[h.unique_id for h in hominids_sorted])
        # Distribute extra food among hungry hominids
        for hominid in hominids_sorted:

            if extra_food_weight <=0 or extra_food_cal <= 0:
                break  # All extra food was distributeda
            # Check if the hominid is hungry
            if hominid.caloric_need > 0 or hominid.gut <= hominid.MAX_GUT_CAPACITY:
                # Determine how much food this hominid will receive

                food_to_give_cal = min(extra_food_cal, hominid.caloric_need)
                food_to_give_weight = min(extra_food_weight, hominid.MAX_GUT_CAPACITY)
                print("hominid ",hominid.unique_id, "will receive ", food_to_give_cal, "calories and ",food_to_give_weight, "grams of food")
                #print("hominid ",hominid.unique_id, "will receive ", food_to_give_weight, "grams of food")
                
                # Give food to hominin
                hominid.gut += food_to_give_weight
                hominid.caloric_need -= food_to_give_cal
                # Uptade food amount
                extra_food_weight -= food_to_give_weight
                extra_food_cal -= food_to_give_cal 
