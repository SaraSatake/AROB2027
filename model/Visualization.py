import sys
import numpy
from numpy import genfromtxt
import matplotlib.pyplot as plt
import pygame
import numpy as new_position

class Visualization():

  def __init__(self, width, height):
    pygame.init()
    self.screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Hominins Simulation")
    self.clock = pygame.time.Clock()
    self.running = True
    self.screen.fill("black")
    
   
    self.cell_width = self.screen.get_width() / 100  # 1280 / 100 = 12.8
    self.cell_height = self.screen.get_height() / 100  # 720 / 100 = 7.2

  def DrawPyGame(self,retorno_grid, Map):
    
    image_channel = pygame.image.load('Images/texture.jpg')

    image_unflooded = pygame.image.load('Images/grass.jpg')

    image_flooded = pygame.image.load('Images/mud.jpg')

    image_plantA = pygame.image.load('Images/combretum.png')
    image_plantB = pygame.image.load('Images/Dobera.png')
    image_plantC = pygame.image.load('Images/tamarindus.png')
    image_plantD = pygame.image.load('Images/Vangueria.png')

    image_hut = pygame.image.load('Images/hut2.jpg').convert()
    image_hut.set_colorkey((255, 255, 255))

    image_hominid = pygame.image.load('Images/hominid.jpeg')

    image_hyena = pygame.image.load('Images/hyena.png')

    image_crocodile = pygame.image.load('Images/crocodile.png')

    # Redimensiona a imagem para novas dimensões
    new_width = 13  # Nova largura
    new_height = 8  # Nova altura

    image_channel = pygame.transform.scale(image_channel, (new_width, new_height))
    image_unflooded = pygame.transform.scale(image_unflooded, (new_width, new_height))
    image_flooded = pygame.transform.scale(image_flooded, (new_width, new_height))
    image_plantA = pygame.transform.scale(image_plantA, (new_width, new_height))
    image_plantB = pygame.transform.scale(image_plantB, (new_width, new_height))
    image_plantC = pygame.transform.scale(image_plantC, (new_width, new_height))
    image_plantD = pygame.transform.scale(image_plantD, (new_width, new_height))
    image_hut = pygame.transform.scale(image_hut, (new_width, new_height))
    image_hominid = pygame.transform.scale(image_hominid, (new_width, new_height))
    image_hyena = pygame.transform.scale(image_hyena, (new_width, new_height))
    image_crocodile = pygame.transform.scale(image_crocodile, (new_width, new_height))

    for coord in retorno_grid.gridVisualization.coord_iter():
        coordenada, conteudo, tipo = coord[1], coord[0], retorno_grid.gridVisualization.get_coord_attribute(coord[1])

        x_pos = int(coordenada[0] * self.cell_width + self.cell_width / 2)  # Centro da célula
        y_pos = int(coordenada[1] * self.cell_height + self.cell_height / 2)  # Centro da célula

        if tipo == 'Unflooded':
            self.screen.blit(image_unflooded, (x_pos, y_pos))
                
        elif tipo == 'Flooded':
            self.screen.blit(image_flooded, (x_pos, y_pos))

        elif tipo == 'Channel':
            self.screen.blit(image_channel, (x_pos, y_pos))

        
        elif tipo == 'PlantA':
            self.screen.blit(image_plantA, (x_pos, y_pos))
        elif tipo == 'PlantB':
            self.screen.blit(image_plantB, (x_pos, y_pos))
        elif tipo == 'PlantC':
            self.screen.blit(image_plantC, (x_pos, y_pos))
        elif tipo == 'PlantD':
            self.screen.blit(image_plantD, (x_pos, y_pos))    


        elif tipo == 'Nest':
            self.screen.blit(image_hut, (x_pos, y_pos))       

        elif tipo == 'Hominid':
            self.screen.blit(image_hominid, (x_pos, y_pos))
        
        elif tipo == 'Hyena':
            self.screen.blit(image_hyena, (x_pos, y_pos))
        
        elif tipo == 'Crocodile':
            self.screen.blit(image_crocodile, (x_pos, y_pos))    

    if Map == 1:
        pygame.display.set_caption("HeatMap")
        max_visits = 0
        for coord in retorno_grid.gridHeatMap.coord_iter():
            visitas = retorno_grid.gridHeatMap.get_coord_attribute(coord[1])  # Obtém o valor da célula
            if isinstance(visitas, int):  # Garantir que seja um número
                max_visits = max(max_visits, visitas)

        # Renderizando o heatmap
        for coord in retorno_grid.gridHeatMap.coord_iter():
            coordenada = coord[1]
            visits = int(retorno_grid.gridHeatMap.get_coord_attribute(coordenada))  # Valor do grid para a célula
            x_pos = int(coordenada[0] * self.cell_width + self.cell_width / 2)  # Centro da célula
            y_pos = int(coordenada[1] * self.cell_height + self.cell_height / 2)  # Centro da célula

            if visits > 0 and max_visits > 0:
                # Calcular a intensidade da cor com base em `visits`
                intensity = int((visits / max_visits) * 255)
                color = (intensity, 0, 0)  # Tons de vermelho
                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(x_pos, y_pos, self.cell_width, self.cell_height)
                )
        
    elif Map == 2:
        pygame.display.set_caption("Positive Pheromone")
        max_visits = 0
        for coord in retorno_grid.gridPheromone.coord_iter():
            visitas = retorno_grid.gridPheromone.get_coord_attribute(coord[1])  # Obtém o valor da célula
            if isinstance(visitas, int):  # Garantir que seja um número
                max_visits = max(max_visits, visitas)

        for coord in retorno_grid.gridPheromone.coord_iter():
            coordenada = coord[1]
            x_pos = int(coordenada[0] * self.cell_width + self.cell_width / 2)  # Centro da célula
            y_pos = int(coordenada[1] * self.cell_height + self.cell_height / 2)
            
            visits = int(retorno_grid.gridPheromone.get_coord_attribute(coordenada))
            if visits > 0 and max_visits > 0:
                # Calcular a intensidade da cor com base em `visits`
                intensity = int((visits / max_visits) * 255)
                color = (120, 40, abs(intensity - 255))  # Tons de vermelho
                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(x_pos, y_pos, self.cell_width, self.cell_height)
                )   
    elif Map == 3:
        pygame.display.set_caption("Dangerous Pheromone")
        max_visits = 0
        for coord in retorno_grid.gridDangerousPheromone.coord_iter():
            visitas = retorno_grid.gridDangerousPheromone.get_coord_attribute(coord[1])  # Obtém o valor da célula
            if isinstance(visitas, int):  # Garantir que seja um número
                max_visits = max(max_visits, visitas)

        for coord in retorno_grid.gridDangerousPheromone.coord_iter():
            coordenada = coord[1]
            x_pos = int(coordenada[0] * self.cell_width + self.cell_width / 2)  # Centro da célula
            y_pos = int(coordenada[1] * self.cell_height + self.cell_height / 2)
            
            visits = int(retorno_grid.gridDangerousPheromone.get_coord_attribute(coordenada))
            if visits > 0 and max_visits > 0:
                # Calcular a intensidade da cor com base em `visits`
                intensity = int((visits / max_visits) * 255)
                color = (abs(intensity - 255), 0, 0)  # Tons de vermelho
                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(x_pos, y_pos, self.cell_width, self.cell_height)
                )
    elif Map == 4:
        gridSumPheromone = retorno_grid.gridCalculusPheromone  # Novo grid ou use outro nome para o grid de soma

        negativeNumber = False

        # Iterar sobre as coordenadas de um dos grids (por exemplo, gridDangerousPheromone)
        for coord in retorno_grid.gridDangerousPheromone.coord_iter():
            coordenada = coord[1]
            
            # Obter o valor dos feromônios nos dois grids nas mesmas coordenadas
            pheromone_value = int(retorno_grid.gridPheromone.get_coord_attribute(coordenada))  # Valor do grid normal
            dangerous_pheromone_value = int(retorno_grid.gridDangerousPheromone.get_coord_attribute(coordenada))  # Valor do grid perigoso
            
            # Somar os valores
            summed_value = pheromone_value - dangerous_pheromone_value
            
            if summed_value < 0:
                negativeNumber = True

            # Colocar o valor somado no novo grid
            gridSumPheromone.add_coord_attribute(coordenada, summed_value)

        if negativeNumber:
            pygame.display.set_caption("Compensed Pheromone")
            max_visits = 0
            for coord in gridSumPheromone.coord_iter():
                visitas = gridSumPheromone.get_coord_attribute(coord[1])  # Obtém o valor da célula
                if isinstance(visitas, int):  # Garantir que seja um número
                    max_visits = max(max_visits, visitas)

            for coord in gridSumPheromone.coord_iter():
                coordenada = coord[1]
                x_pos = int(coordenada[0] * self.cell_width + self.cell_width / 2)  # Centro da célula
                y_pos = int(coordenada[1] * self.cell_height + self.cell_height / 2)
                
                visits = int(gridSumPheromone.get_coord_attribute(coordenada))
                if visits > 0 and max_visits > 0:
                    # Calcular a intensidade da cor com base em `visits`
                    intensity = int((visits / max_visits) * 255)
                    color = (120, 40, abs(intensity - 255))  # Tons de vermelho
                    pygame.draw.rect(
                        self.screen,
                        color,
                        pygame.Rect(x_pos, y_pos, self.cell_width, self.cell_height)
                    )  

            min_visits = 0
            for coord in gridSumPheromone.coord_iter():
                visitas = gridSumPheromone.get_coord_attribute(coord[1])  # Obtém o valor da célula
                if isinstance(visitas, int):  # Garantir que seja um número
                    min_visits = min(min_visits, visitas) 

            for coord in gridSumPheromone.coord_iter():
                coordenada = coord[1]
                x_pos = int(coordenada[0] * self.cell_width + self.cell_width / 2)  # Centro da célula
                y_pos = int(coordenada[1] * self.cell_height + self.cell_height / 2)
                
                visits = int(gridSumPheromone.get_coord_attribute(coordenada))
                if visits < 0 and min_visits < 0:
                    # Calcular a intensidade da cor com base em `visits`
                    intensity = int((visits / min_visits) * 255)
                    color = (abs(intensity - 255), 0, 0)  # Tons de vermelho
                    pygame.draw.rect(
                        self.screen,
                        color,
                        pygame.Rect(x_pos, y_pos, self.cell_width, self.cell_height)
                    )  
        else:
            pygame.display.set_caption("Compensed Pheromone")
            max_visits = 0
            for coord in gridSumPheromone.coord_iter():
                visitas = gridSumPheromone.get_coord_attribute(coord[1])  # Obtém o valor da célula
                if isinstance(visitas, int):  # Garantir que seja um número
                    max_visits = max(max_visits, visitas)

            for coord in gridSumPheromone.coord_iter():
                coordenada = coord[1]
                x_pos = int(coordenada[0] * self.cell_width + self.cell_width / 2)  # Centro da célula
                y_pos = int(coordenada[1] * self.cell_height + self.cell_height / 2)
                
                visits = int(gridSumPheromone.get_coord_attribute(coordenada))
                if visits > 0 and max_visits > 0:
                    # Calcular a intensidade da cor com base em `visits`
                    intensity = int((visits / max_visits) * 255)
                    color = (120, 40, abs(intensity - 255))  # Tons de vermelho
                    pygame.draw.rect(
                        self.screen,
                        color,
                        pygame.Rect(x_pos, y_pos, self.cell_width, self.cell_height)
                    )  


    else:
        pygame.display.set_caption("Hominins Simulation")

    pygame.display.flip()