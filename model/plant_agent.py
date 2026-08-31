import mesa
import numpy as np
from pathlib import Path
import math
import random



grid = np.zeros((100, 100))

class PlantAgent(mesa.Agent):
    """
    Simplified Plant agent: 
    - Location (x,y), random start location
    - Stage 
      - Growth: Add one fruit per day
      - Stasis: Do not add fruits
      - Decay: Delete one fruit per day
      - Dormancy: Does nothing
    - Current Fruits
    - Fruit Weight, Fruit Calories
    """
   
    def __init__(self, unique_id, model, type_plant, fruit_weigth, fruit_calories, K, r, listPossibleCoordinates):
        super().__init__(unique_id, model)

        self.agent_type = type_plant

        # Plant Location
        while True:
            cluster = self.random.choice(listPossibleCoordinates)
            x, y = self.random.choice(cluster)
            if self.agent_type == 'plantA':
                if model.grid.get_coord_attribute((x,y)) == 'Flooded':
                    break
            else:
                if model.grid.get_coord_attribute((x,y)) == 'Unflooded' or model.grid.get_coord_attribute((x,y)) == 'Flooded':
                    break

        self.start_location = (x,y)
        #print(self.agent_type," - ",self.unique_id, " at ", self.start_location)
  
        
        
     

        # Plant States:
        self.state = 0 # initial state
        self.fruits = random.randint(int(0.3 * K), int(0.5 * K))
        # lenght of each state in days (maybe in steps is better?)
        self.state_length = [20,30,20,10] 
        self.state_count = 0

        # Fruit Weight and calories - These values are arbitrary!
        self.fruit_weigth = fruit_weigth
        self.fruit_calories = fruit_calories

        # Verhulst equation variables
        self.K = K  # Maximum carrying capacity of fruits
        self.r = r  # Growth rate

        # Log attributes
        self.available_calories = self.fruit_calories * self.fruits
        self.total_spoiled = 0
    
    

    def get_portion(self):
        # an agent gets a portion from this fruit. Returns calories and weight
        if self.fruits > 0:
            self.fruits -= 1
            self.available_calories = self.fruit_calories * self.fruits
            #print("Plant", self.unique_id, "has", self.available_calories, "calories remaining after portion consumed.")
            return self.fruit_calories, self.fruit_weigth
        else:
            #print("Plant ",self.unique_id, "has no fruits.")
            return 0, 0

    def plant_growth_equation(self, N):
        # Verhulst equation
        return N + self.r * N * (1 - N / self.K)



    def step(self):
        # Plant agent only acts once a day - FIXME: can be done better?
        if self.model.time % self.model.DAY_LENGTH != 0:
            return

        if self.state == 0:  # add a fruit per day if growing
            self.fruits = max(1, self.fruits + round(self.plant_growth_equation(self.fruits)))  # Ensure at least 1 fruit 
        if self.state == 2:  # remove fruits on decay
            # Log attribute: Fruits spoiled in this tree
            if self.fruits > 0:
                decay_factor = 0.3  # Percentage of fruits that decay per step
                decayed_fruits = max(1, round(self.fruits * decay_factor))
                self.fruits -= decayed_fruits
                self.total_spoiled += decayed_fruits

        # Log attribute: Total calories available here
        self.available_calories = self.fruit_calories * self.fruits
        #print("Plant ", self.unique_id," has ",self.fruits, " fruits, and ",self.available_calories," calories.")
        self.state_count += 1

        if self.state_count > self.state_length[self.state]: 
            # change state
            self.state = (self.state + 1) % 4
            #print("Current state of plant ",self.unique_id,": ",self.state)
            self.state_count = 0



       