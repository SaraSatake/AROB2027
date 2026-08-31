import mesa
from mesa import model
import numpy as np
from pathlib import Path
from .plant_agent import PlantAgent
import math
import csv
from mesa.datacollection import DataCollector
import pandas as pd
import shutil
from scipy.spatial.distance import euclidean
import random


#Create a grid and external files for visualization and logs 
grid = np.zeros((100, 100))
gridPath = np.zeros((100, 100))
gridHeatMap = np.zeros((100, 100))
gridHeatMapExplorers = np.zeros((100, 100))
gridHeatMapFollowers = np.zeros((100, 100))
gridPheromone = np.zeros((100, 100))

#log = open("loghominid.txt", "w")
df = pd.DataFrame([[0]*100]*101)



num_rows, num_cols = df.shape

numberHominids = 0
listHomin = []
listNest = []

a = 1
c = 0.7

class HominidAgent(mesa.Agent):
    """An agent that update status once per day"""
   
    def __init__(self, unique_id, model, hominin_type, nest):
        super().__init__(unique_id, model)
        self.agent_type = "hominid"
        self.nest_id = None
        
        self.hominin_type = hominin_type
        
        self.nest = nest
        
        self.addToList()
        

        # Agent Location:
        
        self.start_location = nest.get_position()
        self.last_feed_place = self.start_location 
        #grid[x][y] = 2
        print("Hominid" +str(unique_id)+" starts starts at"+str(self.start_location))

        
        
       
        self.model.gridHeatMap.add_coord_attribute(self.start_location, int(self.model.gridHeatMap.get_coord_attribute(self.start_location)) + 1)

        #Heatmap by type
        if self.hominin_type == "hominin_explorer":
            self.model.gridHeatMapExplorers.add_coord_attribute(
                self.start_location,
                int(self.model.gridHeatMapExplorers.get_coord_attribute(self.start_location)) + 1
            )

        elif self.hominin_type == "hominin_follower":
            self.model.gridHeatMapFollowers.add_coord_attribute(
                self.start_location,
                int(self.model.gridHeatMapFollowers.get_coord_attribute(self.start_location)) + 1
            )
    
        #log.write("Hominid " +str(unique_id)+" starts at "+str(self.start_location)+"\n")
        #print("Hominid " +str(unique_id)+" starts at "+str(self.start_location)+"\n")
       
        #print("------")
       
    

        self.DAILY_CALORIC_NEED = 2500 # Calories needed per day
        self.MAX_GUT_CAPACITY = 1000   # Maximum food weight per day
        self.GLOBAL_MAX_REP_PHEROMONE = 90259 # this value is an avarege maximum pheromone obtained in 10 runs
        self.GLOBAL_MAX_ATTR_PHEROMONE = 44724 # this value is an avarege maximum pheromone obtained in 10 runs

        self.MAX_CARRY_CAPACITY = 5000 
        self.caloric_need = self.DAILY_CALORIC_NEED
        self.gut = 0

        self.carrying_weight = 0
        self.carrying_cal = 0

        
        self.teste = 0
        self.active = True

        self.satiated = False

        self.gathering_food = False

        self.active_good_pheromone = True   
        self.active_dangerous_pheromone = False

        #log.write("Hominid " +str(self.unique_id)+" needs "+str(self.caloric_need)+"calories and there are "+str(self.gut) +" grams of food in the gut. \n")
        #print("Hominid " +str(self.unique_id)+" needs "+str(self.caloric_need)+" calories and there are "+str(self.gut) +" grams of food in the gut. \n")


        # Log variables
        self.fruits_eaten = 0
        self.carcasses_eaten = 0
        self.missed_calories = 0
        self.hominids_under_caloric_need = []
        self.count_attack = 0
        self.calories_consumed_today = 0

        self.total_collected_calories = 0

        self.visited_cells = set()
        self.visited_cells_gathering_food = set()
    
        self.trajectory_gathering_food = []
        self.moves_gathering_food = 0
        self.trajectory = []

        self.pheromone_deposit_count = 0
        self.attr_pheromone_guided_moves = 0
        self.rep_pheromone_guided_moves = 0

           
    def addToList(self):
        listHomin.append(self)

    def get_available_nests(self):
        
        available_nests = []

        for agent in self.model.schedule.agents:
            if isinstance(agent, NestAgent):
                available_nests.append(agent)

        return available_nests

    def step(self):
        
        for i in range(1,numberHominids):
            with open("totalPathHominid"+str(i)+".csv", "w") as arquivo:
                pass
        
        
                 
        if self.model.time % self.model.DAY_LENGTH == 0:
            
            # Things that happened at the start of the day:
            print("--------Start of Day ", self.model.time // self.model.DAY_LENGTH," of Hominid " ,self.unique_id,"-----------")
            print("Current position of Hominid ",self.unique_id,": ", self.pos)

                
            
            self.model.gridHeatMap.add_coord_attribute(self.pos, int(self.model.gridHeatMap.get_coord_attribute(self.pos)) + 1)

                #Heatmap by type
            if self.hominin_type == "hominin_explorer":
                self.model.gridHeatMapExplorers.add_coord_attribute(
                    self.pos,
                    int(self.model.gridHeatMapExplorers.get_coord_attribute(self.start_location)) + 1
                )

            elif self.hominin_type == "hominin_follower":
                self.model.gridHeatMapFollowers.add_coord_attribute(
                    self.pos,
                    int(self.model.gridHeatMapFollowers.get_coord_attribute(self.start_location)) + 1
                )
            
            

            with open("totalPath.csv", mode='w', newline='') as file_csv:
                writer_csv = csv.writer(file_csv)
                for line in gridPath:
                    writer_csv.writerow(line)
            # Update summary variables:
         
            if self.caloric_need > 0:
                self.missed_calories += self.caloric_need # log agents going hungry
                print("Hominid ",self.unique_id, "missed ",self.missed_calories, "calories yesterday.")
                self.hominids_under_caloric_need.append(self)

            for hominid in self.hominids_under_caloric_need:
                print("Hominid", hominid.unique_id, "didn't meet the minimum caloric requirement.")

            
            self.missed_calories = 0
            #print("---Last place that Hominid ", self.unique_id," ate:" , self.last_feed_place)
            #Hominids start in the nest 
            #self.moveToNest()
            
            # Reset gut capacity and calories to 0, set agents to active
            self.caloric_need = self.DAILY_CALORIC_NEED
            self.gut = 0
            self.hominids_under_caloric_need = []
            self.active = True
            self.gathering_food = False

            self.carrying_weight = 0
            self.carrying_cal = 0

            

        # If agent is active, do something:
        if self.active:
    
            food_list = self.encounter_check()
            #print("Hominid ", self.unique_id, "gut: ", self.gut)
            if len(food_list) > 0: # agent finds food in same cell

                    
                
                #print("Hominid " + str(self.unique_id) + " is eating food at " + str(self.pos) + ":")

                self.model.gridHeatMap.add_coord_attribute(self.pos, int(self.model.gridHeatMap.get_coord_attribute(self.pos)) + 1)
                
                    #Heatmap by type
                if self.hominin_type == "hominin_explorer":
                    self.model.gridHeatMapExplorers.add_coord_attribute(
                        self.pos,
                        int(self.model.gridHeatMapExplorers.get_coord_attribute(self.pos)) + 1
                    )

                elif self.hominin_type == "hominin_follower":
                    self.model.gridHeatMapFollowers.add_coord_attribute(
                        self.pos,
                        int(self.model.gridHeatMapFollowers.get_coord_attribute(self.pos)) + 1
                    )
                
                self.last_feed_place = self.pos
                for food in food_list:
                    foodType = getattr(food, 'agent_type')
                    idFood = getattr(food, 'unique_id')
                    #print("- It is a :",foodType, ", ID: ", idFood)

                # If there is food, agent eats until calories or gut are filled
    
                while len(food_list) > 0 and self.caloric_need > 0:
                    s = food_list[0]
                    cal, weight = s.get_portion()
                    self.gut += weight
                    self.caloric_need -= cal
                    #print("Last place that Hominid ", self.unique_id," ate:" , self.last_feed_place)
                    gridPath[self.pos[0]][self.pos[1]] = self.unique_id

                    # returns cal == 0 if food source is exausted
                    if cal == 0:
                        food_list.pop(0)
                        #print("Food exausted")
                print("Hominid ",self.unique_id, "has", self.gut, "in the gut and still needs: ", self.caloric_need)        
                
                # Agent is satisfied
                if self.caloric_need <= 0:
                    self.active = False
                    self.gathering_food = True
                    print("Hominid ",self.unique_id, self.hominin_type, "is satisfied,because the caloric need is ", self.caloric_need,". Now he can start collecting food!") ### if it collects food
                    
                    if not self.active_good_pheromone:
                        print("Hominin ",self.unique_id, " is satisfied and just goes to nest.")
                        self.model.grid.move_agent(self, self.nest.pos)
                        old_pos = self.pos
                        self.model.gridVisualization.add_coord_attribute(old_pos, self.model.grid.get_coord_attribute(old_pos))
                        print("Homiinid ",self.unique_id, "went to nest",self.pos)
                    
                    else:    
                        print("Hominid ",self.unique_id, "is satisfied. Now he can spread pheromone!")
                        #self.model.grid.move_agent(self, self.start_location) # TODO: Replace with NEST

                        neighbors = self.model.gridPheromone.get_neighborhood(
                        self.pos,
                        moore=True,  # Consider 8 neighbors
                        include_center=True,
                        radius=100
                        )

                        
                        for neighbor_pos in neighbors:
                            #Calculate the distance from the hominid to its neighbor.
                            distance = euclidean(neighbor_pos, self.pos)
                            
                            #Gaussian calculation

                            pheromone = a * (np.exp((-distance**2)/2*c**2)) 

                            pheromone *= 10000

                            newpheromone = pheromone + int(self.model.gridPheromone.get_coord_attribute(neighbor_pos))

                            #store pheromone
                            self.model.gridPheromone.add_coord_attribute(neighbor_pos, int(newpheromone))

                        self.pheromone_deposit_count += 1


                        #log.write("Hominid " +str(self.unique_id)+" is satisfied and is going back to the nest. \n") #write to log
                        #print("Hominid " +str(self.unique_id)+" is satisfied and is going back to the nest. \n") #write to log
                        #print("Homiinid ",self.unique_id, "is now at nest",self.pos)
                        old_pos = self.pos
                        #self.model.grid.move_agent(self, self.nest.pos) # in case, the hominin needs to go back to the nest
                        print("Homiinid ",self.unique_id, "will start gathering food from ",self.pos)
                        self.model.gridVisualization.add_coord_attribute(old_pos, self.model.grid.get_coord_attribute(old_pos))
                        # print("Hominid ",self.unique_id, "is satiated and started to gather food" )
                        self.satiated = True
                    
                   
                    
            else:
                self.move()

            
            # Else, scan for food (adjacent cells)
              # if food is detected, move to food
              # else, move randomly
        else:
            if self.gathering_food:
                self.gather_food()
            
        
        if (self.model.time + 1) % self.model.DAY_LENGTH == 0:
            #Things that happened at the end of the day
            #self.model.grid.move_agent(self, self.start_location) #move hominids back to the nest
            if self.carrying_weight > 0 and self.carrying_weight < self.MAX_CARRY_CAPACITY:
                print("At the end of the day, Hominid ",self.unique_id, "collected  ",self.carrying_weight,"grams and ",self.carrying_cal,"cal")
                self.total_collected_calories = self.carrying_cal
                print("Nest ",self.nest.unique_id, "has ",self.carrying_cal," of extra calories")
                self.nest.add_extra_food(self.carrying_weight, self.carrying_cal)
            if self.caloric_need > 0:
                print("Hominid ",self.unique_id, "starved today.")
            
            self.teste = self.caloric_need
            
            self.calories_consumed_today = self.DAILY_CALORIC_NEED - self.caloric_need
            #print("caloric no hominid: ",self.teste)
            print("Hominid ", self.unique_id, "consumed", self.calories_consumed_today, "calories today.")
            #print("Hominid ", self.unique_id, "caloric need was", self.caloric_need, "calories today.")
            print("-------- End of Day:", self.model.time // self.model.DAY_LENGTH, " of Hominid ",self.unique_id,"-----------")                   
  
    def moveToNest(self):
        self.model.gridVisualization.add_coord_attribute(self.pos, self.model.grid.get_coord_attribute(self.pos))
        self.model.grid.move_agent(self, self.start_location)
        self.model.gridVisualization.add_coord_attribute(self.start_location, 'Hominid')

    def encounter_check(self):
        _cellmates = self.model.grid.get_cell_list_contents([self.pos])
        cell_food = [i for i in _cellmates if i.agent_type in ["plantA", "plantB", "plantC", "plantD"] and i.available_calories > 0]

        for food in cell_food:
            idFood = getattr(food, 'unique_id')
            available_calories = getattr(food, 'available_calories')
            available_fruits = getattr(food, 'fruits')
            #print("Plant ID:", idFood, "Available fruits: ",available_fruits, "- Available Calories:", available_calories)

        return cell_food

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore = True, # 8 neighbors
                include_center = False
            )
        old_pos = self.pos
        #print("Hominid ",self.unique_id, "current position: ",self.pos)
        #print("Hominid ",self.unique_id, "Possible neighbors: ")
        # for cell in possible_steps:
        #     print(cell)
        # Check for food nearby. TODO: Check for correctness / Speed
        def has_food(cell):

            cell_contents = self.model.grid.get_cell_list_contents([cell])    

            for content in cell_contents:
                if content.agent_type == "plantA" and content.available_calories > 0:
                    return True
                elif content.agent_type == "plantB" and content.available_calories > 0:
                    return True
                elif content.agent_type == "plantC" and content.available_calories > 0:
                    return True 
                elif content.agent_type == "plantD" and content.available_calories > 0:
                    return True             
    
            return False 

        food_cells = [c for c in possible_steps if has_food(c)]

        def has_dangerous_animal(cell):

            cell_contents = self.model.grid.get_cell_list_contents([cell])    

            for content in cell_contents:
                if content.agent_type == "hyena":
                    print("hominid ",self.unique_id, "caloric need before: ",self.caloric_need)
                    print("hominid ",self.unique_id, "was attacked by a hyena and lost 100 kcal.")
                    self.caloric_need = self.caloric_need + 100
                    print("hominid ",self.unique_id, "caloric need after: ",self.caloric_need)
                    self.count_attack = self.count_attack + 1
                    print("attack: ",self.count_attack, "hominid ",self.unique_id)
                    return True
                elif content.agent_type == "crocodile":
                    print("hominid ",self.unique_id, "caloric need before: ",self.caloric_need)
                    print("hominid ",self.unique_id, "was attacked by a crocodyle and lost 100 kcal")
                    self.caloric_need = self.caloric_need + 100
                    print("hominid ",self.unique_id, "caloric need after: ",self.caloric_need)
                    self.count_attack = self.count_attack + 1
                    print("attack: ",self.count_attack, "hominid ",self.unique_id)
                    return True
    
            return False

        dangerous_animal_cells = [c for c in possible_steps if has_dangerous_animal(c)]

        if len(food_cells) > 0:
            for cell in food_cells:
                #Get agents in the cell
                agents_in_cell = self.model.grid.get_cell_list_contents([cell])
                for agent in agents_in_cell:
                    # Verifies if it is a plant
                    if isinstance(agent, PlantAgent):
                        available_fruits = agent.fruits
                        #print("Plant at", cell, "with", available_fruits, "fruits available")    
            
        if self.active_dangerous_pheromone:
            if len(dangerous_animal_cells) > 0:
                
                neighbors = self.model.gridDangerousPheromone.get_neighborhood(
                        self.pos,
                        moore=True,  # Consider 8 neighbors
                        include_center=True,
                        radius=100
                        )

                for neighbor_pos in neighbors:
                    #Calculate the distance from the hominid to its neighbor.
                    distance = euclidean(neighbor_pos, self.pos)
                    
                    #Gaussian calculation

                    pheromone = a * (np.exp((-distance**2)/2*c**2)) 

                    pheromone *= 10000

                    newpheromone = pheromone + int(self.model.gridDangerousPheromone.get_coord_attribute(neighbor_pos))

                    #store pheromone
                    self.model.gridDangerousPheromone.add_coord_attribute(neighbor_pos, int(newpheromone))
                
                
                #new_position = self.probabilitic_choice(possible_steps)
                
                #new_position = self.deterministic_choice(possible_steps)

                new_position = self.heuristic_choice(possible_steps)    
                
            #print("Hominid ",self.unique_id, " chose to eat/get in ", new_position)
            else:
            

                #new_position = self.probabilistic_choice_with_dangerous_pheromone(possible_steps)

                #new_position = self.deterministic_choice_with_dangerous_pheromone(possible_steps)

                new_position = self.heuristic_choice_with_dangerous_pheromone(possible_steps)

                #print("Hominid ",self.unique_id, " chose to go to ", new_position)
        else:
              
            
            #new_position = self.probabilistic_choice_with_dangerous_pheromone(possible_steps)
            
            #new_position = self.deterministic_choice_with_dangerous_pheromone(possible_steps)

            new_position = self.heuristic_choice_with_dangerous_pheromone(possible_steps)

                 
        
        #new_position = self.random.choice(possible_steps)
        if self.model.time % 3 == 0:
            self.model.grid.move_agent(self, new_position)
            
            if self.gathering_food:
                self.moves_gathering_food += 1
                self.visited_cells_gathering_food.add(new_position)
                self.trajectory_gathering_food.append(new_position)

                self.model.gridVisualization.add_coord_attribute(old_pos, self.model.grid.get_coord_attribute(old_pos))
                self.model.gridVisualization.add_coord_attribute(new_position, 'Hominid')
            else:    
                #Keeping the visited cells   
                self.visited_cells.add(new_position)
                self.trajectory.append(new_position)

                self.model.gridVisualization.add_coord_attribute(old_pos, self.model.grid.get_coord_attribute(old_pos))
                self.model.gridVisualization.add_coord_attribute(new_position, 'Hominid')
                #self.gridVisualization.add_coord_attribute(new_position, 'Hominid')

                    
                # General heatmap
                self.model.gridHeatMap.add_coord_attribute(new_position, int(self.model.gridHeatMap.get_coord_attribute(self.pos)) + 1)
            
                #Heatmap by type
                if self.hominin_type == "hominin_explorer":
                    self.model.gridHeatMapExplorers.add_coord_attribute(
                        new_position,
                        int(self.model.gridHeatMapExplorers.get_coord_attribute(self.pos)) + 1
                    )

                elif self.hominin_type == "hominin_follower":
                    self.model.gridHeatMapFollowers.add_coord_attribute(
                        new_position,
                        int(self.model.gridHeatMapFollowers.get_coord_attribute(self.pos)) + 1
                    )


    def gather_food(self):

        if self.gathering_food:
            food_list = self.encounter_check()
            #print("Hominid ", self.unique_id, "is carrying: ", self.carrying_weight)
            if len(food_list) > 0: # agent finds food in same cell


                print("Hominid " + str(self.unique_id) + " collecting food at " + str(self.pos) + ":")

                self.model.gridHeatMap.add_coord_attribute(self.pos, int(self.model.gridHeatMap.get_coord_attribute(self.pos)) + 1)

                #Heatmap by type
                if self.hominin_type == "hominin_explorer":
                    self.model.gridHeatMapExplorers.add_coord_attribute(
                        self.pos,
                        int(self.model.gridHeatMapExplorers.get_coord_attribute(self.pos)) + 1
                    )

                elif self.hominin_type == "hominin_follower":
                    self.model.gridHeatMapFollowers.add_coord_attribute(
                        self.pos,
                        int(self.model.gridHeatMapFollowers.get_coord_attribute(self.pos)) + 1
                    )

                gridHeatMap[self.pos[0]][self.pos[1]] = 1 + gridPath[self.pos[0]][self.pos[1]]
                for food in food_list:
                    foodType = getattr(food, 'agent_type')
                    idFood = getattr(food, 'unique_id')
                    #print("- It is a :",foodType, ", ID: ", idFood)

                # If there is food, agent eats until calories or gut are filled

                while len(food_list) > 0 and self.carrying_weight < self.MAX_CARRY_CAPACITY:
                    s = food_list[0]
                    cal, weight = s.get_portion()
                    self.carrying_weight += weight
                    self.carrying_cal += cal
                
                    gridPath[self.pos[0]][self.pos[1]] = self.unique_id

                    # returns cal == 0 if food source is exausted
                    if cal == 0:
                        food_list.pop(0)
                        #print("Food exausted")
                #print("Hominid ",self.unique_id, "is carrying", self.carrying_weight, "grams, and can still carry ", self.MAX_CARRY_CAPACITY - self.carrying_weight)        
                # If agent is satisfied, go back to the nest
                if self.carrying_weight>= self.MAX_CARRY_CAPACITY:
                    
                    print("Hominid ",self.unique_id, "can't carry food anymore.")
                    self.model.gridVisualization.add_coord_attribute(self.pos, self.model.grid.get_coord_attribute(self.pos))
                    self.model.grid.move_agent(self, self.start_location) # TODO: Replace with NEST
                    self.model.gridVisualization.add_coord_attribute(self.start_location, 'Hominid')
                    self.nest.add_extra_food(self.carrying_weight, self.carrying_cal)
                    print("Hominid ",self.unique_id, "put", self.carrying_weight, "g of food in nest ",self.nest.unique_id)
                    print("Nest ",self.nest.unique_id, " now has ",self.nest.extra_food_weight, "g of food, and ", self.nest.extra_food_cal, "cal of food")
                    #log.write("Hominid " +str(self.unique_id)+" is satisfied and is going back to the nest. \n") #write to log
                    #print("Hominid " +str(self.unique_id)+" is satisfied and is going back to the nest. \n") #write to log
                    #print("Homiinid ",self.unique_id, "is now at nest",self.pos)
                    # print("Hominid ",self.unique_id, "is satiated and started to gather food" )
                    self.satiated = True
                    self.gathering_food = False
                    
            else:
                self.move()
                #self.model.gridHeatMap.add_coord_attribute(new_position, int(self.model.gridHeatMap.get_coord_attribute(self.pos)) + 1)
                #Heatmap by type
                if self.hominin_type == "hominin_explorer":
                    self.model.gridHeatMapExplorers.add_coord_attribute(
                        self.pos,
                        int(self.model.gridHeatMapExplorers.get_coord_attribute(self.pos)) + 1
                    )

                elif self.hominin_type == "hominin_follower":
                    self.model.gridHeatMapFollowers.add_coord_attribute(
                        self.pos,
                        int(self.model.gridHeatMapFollowers.get_coord_attribute(self.pos)) + 1
                    )

    def probabilitic_choice(self, possible_steps):

        rouletteList = [] # In this list, we create a roulette with the values of pheromone in the coordinates
        for coordinate in possible_steps:
            if self.model.grid.get_coord_attribute(coordinate) != 'Channel':
                cell_value = self.model.gridPheromone.get_coord_attribute(coordinate)
                cell_value = int(cell_value) + 1
                for _ in range(cell_value):
                    rouletteList.append(coordinate)


        index_random = random.randint(0, len(rouletteList) - 1)
        new_position = rouletteList[index_random]
        return new_position
    
    def probabilistic_choice_with_dangerous_pheromone(self, possible_steps):

        rouletteList = [] # In this list, we create a roulette with the values of pheromone in the coordinates
        calculusPheromoneList = []
        for coordinate in possible_steps:
            if self.model.grid.get_coord_attribute(coordinate) != 'Channel':

                # Get the values ​​from the two pheromone grids at the same indices.
                cell_value_gridPheromone = self.model.gridPheromone.get_coord_attribute(coordinate)
                cell_value_gridDangerousPheromone = self.model.gridDangerousPheromone.get_coord_attribute(coordinate)

                #Calculate the final pheromone by subtracting the two values ​​and place it in the final grid just to be sure.
                cell_value_gridCalculusPheromone = int(cell_value_gridPheromone) - int(cell_value_gridDangerousPheromone)
                self.model.gridCalculusPheromone.add_coord_attribute(coordinate, cell_value_gridCalculusPheromone)
                
                # Add the coordinate and pheromone value to the list.
                calculusPheromoneList.append((coordinate, cell_value_gridCalculusPheromone))
                
        hasNegativeValue = False
        smallestValue = calculusPheromoneList[0][1]  # It starts with the value of the first item.

        for coord, value in calculusPheromoneList:
            if value < 0:
                hasNegativeValue = True  # Mark if there is any negative value.
            if value < smallestValue:
                smallestValue = value

        if hasNegativeValue:
            for i in range(len(calculusPheromoneList)):
                coordinate, value = calculusPheromoneList[i]
                calculusPheromoneList[i] = (coordinate, 1 + abs(smallestValue) + value)
        else:
            for i in range(len(calculusPheromoneList)):
                coordinate, value = calculusPheromoneList[i]
                calculusPheromoneList[i] = (coordinate, 1 + value)

        for coordinate, value in calculusPheromoneList:
            for _ in range(value):
                rouletteList.append(coordinate)

        index_random = random.randint(0, len(rouletteList) - 1)
        new_position = rouletteList[index_random]

        return new_position

    def deterministic_choice(self, possible_steps):

        sum_dx = 0.0
        sum_dy = 0.0
        print("-Current positionn: ",self.pos)
        current_x, current_y = self.pos  # current agent position

        for coordinate in possible_steps:
            if self.model.grid.get_coord_attribute(coordinate) != 'Channel':

                pheromone = self.model.gridPheromone.get_coord_attribute(coordinate)
                pheromone = int(pheromone)

                dx = coordinate[0] - current_x
                dy = coordinate[1] - current_y

                # pheromone-weighted vector sum
                sum_dx += pheromone * dx
                sum_dy += pheromone * dy
                print("Vector sum:", sum_dx, sum_dy)
        if sum_dx != 0 or sum_dy != 0: #if the resulting vectors are not zero

            # normalizes to select only the direction.
            if abs(sum_dx) > abs(sum_dy):
                step_x = int(sum_dx / abs(sum_dx))
                step_y = 0
            elif abs(sum_dy) > abs(sum_dx):
                step_x = 0
                step_y = int(sum_dy / abs(sum_dy))
            else:
                step_x = int(sum_dx / abs(sum_dx))
                step_y = int(sum_dy / abs(sum_dy))

            candidate_position = (current_x + step_x, current_y + step_y)

            if candidate_position in possible_steps:
                print("Chosen direction step:", step_x, step_y)
                print("Candidate position:", (current_x + step_x, current_y + step_y))
                print("Possible steps:", possible_steps)

                new_position = candidate_position
                print("Final chosen position:", new_position)
            else:
                # fallback: choose the best valid alternative
                new_position = random.choice(possible_steps)
                print("There was no possible step and the chosen one was: ",new_position)
        else:
            new_position = random.choice(possible_steps)
            print("null vector, so the chosen one was: ",new_position)
        
        return new_position

    def deterministic_choice_with_dangerous_pheromone(self, possible_steps):

        sum_dx = 0.0
        sum_dy = 0.0
        print("-Current positionn: ",self.pos)
        current_x, current_y = self.pos

        for coordinate in possible_steps:
            if self.model.grid.get_coord_attribute(coordinate) != 'Channel':

                food_pheromone = int(
                    self.model.gridPheromone.get_coord_attribute(coordinate)
                )
                danger_pheromone = int(
                    self.model.gridDangerousPheromone.get_coord_attribute(coordinate)
                )

                # calculate pheromone 
                total_pheromone = food_pheromone - danger_pheromone

                dx = coordinate[0] - current_x
                dy = coordinate[1] - current_y

                # soma vetorial ponderada
                sum_dx += total_pheromone * dx
                sum_dy += total_pheromone * dy
                print("Vector sum:", sum_dx, sum_dy)
        if sum_dx != 0 or sum_dy != 0:

            if abs(sum_dx) > abs(sum_dy):
                step_x = int(sum_dx / abs(sum_dx))
                step_y = 0
            elif abs(sum_dy) > abs(sum_dx):
                step_x = 0
                step_y = int(sum_dy / abs(sum_dy))
            else:
                step_x = int(sum_dx / abs(sum_dx))
                step_y = int(sum_dy / abs(sum_dy))

            candidate_position = (current_x + step_x, current_y + step_y)

            if candidate_position in possible_steps:
                print("Chosen direction step:", step_x, step_y)
                print("Candidate position:", (current_x + step_x, current_y + step_y))
                print("Possible steps:", possible_steps)
                new_position = candidate_position
                print("Final chosen position:", new_position)
            else:
                # fallback: choose the best valid alternative
                new_position = random.choice(possible_steps)
                print("There were no possible steps, so the chosen one was: ",new_position)
        else:
            new_position = random.choice(possible_steps)
            print("Null vector, the chosen one was :",new_position)

        return new_position

    def heuristic_choice(self, possible_steps):

        if self.hominin_type == 'hominin_follower':
            alpha = 1  # limiar  (75% of the global max value)
        else:
            alpha = 0   

        best_coord = None
        best_value = -float("inf")
        attr_values = []
    
        for coordinate in possible_steps:
            if self.model.grid.get_coord_attribute(coordinate) != 'Channel':
                pheromone = float(self.model.gridPheromone.get_coord_attribute(coordinate))

                if pheromone > best_value:
                    best_value = pheromone
                    best_coord = coordinate
        
        
        threshold = alpha * best_value
        
        #print("[DEBUG] best_value:", best_value, "para Hominin ",self.hominin_type)
        #print("[DEBUG] threshold:", threshold, "para Hominin ",self.hominin_type)

        possibles_candidates = []

        for coordinate in possible_steps:
            if self.model.grid.get_coord_attribute(coordinate) != 'Channel':
                pheromone = float(self.model.gridPheromone.get_coord_attribute(coordinate))

                if pheromone >= threshold:
                    possibles_candidates.append(coordinate)
        
        #print("[DEBUG] HEURISTIC EXPLORATION activated")
        new_position = random.choice(possibles_candidates)

        # verify if the movement was guided by pheromone
        chosen_pheromone = float(
        self.model.gridPheromone.get_coord_attribute(new_position)
        )

        if chosen_pheromone > 0:
            self.attr_pheromone_guided_moves += 1

        return new_position
        
    def heuristic_choice_with_dangerous_pheromone(self, possible_steps):
        
        if self.hominin_type == 'hominin_follower':
            alpha = 1  # attraction
            beta = 1    # repulsion
        else:
            alpha = 0  # attraction
            beta = 0   # repulsion
        
        safe_cells = []
        best_attr_score = -float("inf")
        best_attr_coord = None

        best_rep_value = -float("inf")
        worst_rep_coord = None
        attr_values = []
        rep_values  = []

        for coordinate in possible_steps:
            if self.model.grid.get_coord_attribute(coordinate) != 'Channel':

                attr = float(self.model.gridPheromone.get_coord_attribute(coordinate))
                rep  = float(self.model.gridDangerousPheromone.get_coord_attribute(coordinate))
                attr_values.append(attr)
                rep_values.append(rep)


                score = attr - rep

                # best attraction
                if score > best_attr_score:
                    best_attr_score = score
                    best_attr_coord = coordinate
                

        attr_threshold = alpha * best_attr_score
        
        if attr_threshold < 0:
            attr_threshold += best_attr_score

        #print("best_attr_score:", best_attr_score, " para Hominin ",self.hominin_type)
        #print("attr_threshold:", attr_threshold, " para Hominin ",self.hominin_type)

        for coordinate in possible_steps:
            if self.model.grid.get_coord_attribute(coordinate) != 'Channel':
                attr = float(self.model.gridPheromone.get_coord_attribute(coordinate))
                rep = float(self.model.gridDangerousPheromone.get_coord_attribute(coordinate))
                # print("------")
                # print(coordinate)
                # print("attr: ",attr)
                # print("rep: ",rep)
                # print("attr - rep: ",attr - rep)
                if (attr - rep) >= attr_threshold:
                    safe_cells.append(coordinate)
                #     print("alocado ")
                # print("------")


        
        new_position = random.choice(safe_cells)
        # print("new position is ",new_position, " para Hominin ",self.hominin_type)
        # print("---")

        # verify if the moviment was guided by pheromone
        chosen_attr = float(
            self.model.gridPheromone.get_coord_attribute(new_position)
        )

        chosen_rep = float(
            self.model.gridDangerousPheromone.get_coord_attribute(new_position)
        )

        if chosen_attr > 0:
            self.attr_pheromone_guided_moves += 1
            #print("foi guiado por feromonio")

        if any(rep > 0 for rep in rep_values):
            self.rep_pheromone_guided_moves += 1    

        return new_position

class NestAgent(mesa.Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.agent_type = "nest"
        self.hominids = []
        self.underfed_hominids = []
        self.recieved_food_hominids = []
        self.extra_food_weight = 0
        self.extra_food_cal = 0
        self.number_of_underfed_hominids_before_sharing = 0
        self.number_of_underfed_hominids_after_sharing = 0

        while True:
            x = model.random.randrange(model.grid.width)
            y = model.random.randrange(model.grid.height)
            if model.grid.get_coord_attribute((x,y)) == 'Unflooded':
                break
        self.start_location = (x,y)

    def get_position(self):
        return self.pos
    
    def add_hominid(self, hominid):
        
        self.hominids.append(hominid)
        hominid.nest_id = id(self)  # Hominid receives a nest id    
        hominid.nest = self
        
    def add_underfed_hominid_before_sharing_food(self, hominid):
        #print("Nest ",self.unique_id, "received Hominid ",hominid.unique_id)
        self.underfed_hominids.append(hominid)
        self.number_of_underfed_hominids = len(self.underfed_hominids)

    def add_underfed_hominid_after_sharing_food(self, hominid):
        self.underfed_hominids.append(hominid)
        self.number_of_underfed_hominids = len(self.underfed_hominids)    

    def add_extra_food(self, add_extra_food_weight, add_extra_food_cal):
        self.extra_food_weight += add_extra_food_weight
        self.extra_food_cal += add_extra_food_cal    
    
    def reset_extra_food(self):
        self.extra_food_weight = 0
        self.extra_food_cal = 0    