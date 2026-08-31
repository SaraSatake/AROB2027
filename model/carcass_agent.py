import mesa
import numpy as np
from pathlib import Path

grid = np.zeros((20, 20))

class CarcassAgent(mesa.Agent):
    """
    Simplified Carcass agent: 
    - Location (x,y), location is given by the model
    - Size (small, large, medium)
    - Total portions
    - Portion Weight
    - Portion Calories
    """
    
    def __init__(self, unique_id, model, coord, parameters = None):
        super().__init__(unique_id, model)

        self.agent_type = "carcass"

        # Carcass position (in the future, defined by map)
        # x = model.random.randrange(model.grid.width)
        # y = model.random.randrange(model.grid.height)
        self.start_location = coord

        # Carcass type (1- small, 2- medium, 3- large)
        # Values are arbitrary!
        self.size = model.random.choices([1, 2, 3], [10, 5, 1])[0]
        self.portions = 3 ** self.size # 3, 9, 27 portions
        self.portion_weight = 100
        self.portion_calories = 300

        # For spoilage
        self.start_time = model.time

        # Log attributes
        self.available_calories = self.portions * self.portion_calories
        
    def get_portion(self):
        # an agent gets a portion from this carcass. Returns calories and weight

        # Agents can only eat from small carcasses. TODO: allow agents to collaborate
        # For large carcasses
        if self.size == 1:
            if self.portions > 0:
                self.portions -= 1
                self.available_calories = self.portions * self.portion_calories
                return self.portion_calories, self.portion_weight
            # Remove carcass if empty
            else :
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                return 0, 0
        else:
            return 0, 0
    
    def step(self):
        # Carcass spoils after one day has passed

        if (self.model.time - self.start_time) > self.model.DAY_LENGTH:
            if self.size == 3: 
                # large carcasses get smaller
                self.size = 2
                self.portions = min(self.portions, 3**2)
                self.start_time = self.model.time # reset spoiler time
                # TODO: Log the decay somewhere
            else:
                # Medium and small carcasses disappear
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)

                # TODO: Log the decay somewhere
