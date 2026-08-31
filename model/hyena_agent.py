import mesa
from mesa import model
import random

class HyenaAgent(mesa.Agent):
   
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.agent_type = "hyena"
        

        # Agent Location:

        while True:
            x = model.random.randrange(model.grid.width)
            y = model.random.randrange(model.grid.height)
            if model.grid.get_coord_attribute((x,y)) == 'Unflooded':
                break

        self.start_location = x,y
        print(self.agent_type," - ",self.unique_id, " at ", self.start_location)

    def step(self):
            self.move()

    def move(self):

        possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore = True, # 8 neighbors
                include_center = False
            )
        old_pos = self.pos

        possible_steps_to_walk = []
        for i in possible_steps:
            if self.model.grid.get_coord_attribute(i) != 'Channel':
                possible_steps_to_walk.append(i)

        indice_aleatorio = random.randint(0, len(possible_steps_to_walk) - 1)
        new_position = possible_steps_to_walk[indice_aleatorio]   
        self.model.grid.move_agent(self, new_position)
        self.model.gridVisualization.add_coord_attribute(old_pos, self.model.grid.get_coord_attribute(old_pos))
        self.model.gridVisualization.add_coord_attribute(new_position, 'Hyena')            