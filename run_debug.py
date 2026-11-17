from model.world_model import HominidsModel 
from tqdm import tqdm

from collections import Counter
from matplotlib import pyplot

from pathlib import Path

from model.Visualization import *
from model.hominid_agent import *


import os
import csv
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import sys
import random

def save_grid_as_csv(return_grid, filename="grid_table.csv"):
    # Discovering the limits of the grid
    width = return_grid.width
    height = return_grid.height

    # Create a table where each cell corresponds to the value in the grid.
    table = []
    for y in range(height):
        row = []
        for x in range(width):
            coord = (x, y)
            visitas = return_grid.get_coord_attribute(coord)
            row.append(visitas if isinstance(visitas, int) else 0)
        table.append(row)

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(table)

turn_on_visualization = True
turn_on_visualization_heatmap = True    
turn_on_visualization_pheromone = True
turn_on_visualization_dangerous_pheromone = True

num_executions = 1 

all_runs_calories = []
all_runs_fruits = []
all_runs_attacks = []

def EvaporatesPheromone(modelObject, stepCount, stepEvaporation, mu):  
    if stepCount % stepEvaporation == 0:
        for i in range(modelObject.gridPheromone.width):
            for j in range(modelObject.gridPheromone.height):
                coordinate = (i,j)
                if(modelObject.gridPheromone.get_coord_attribute(coordinate) != 0 ):
                    if model.grid.get_coord_attribute((coordinate)) == 'Unflooded': 
                        modelObject.gridPheromone.add_coord_attribute(coordinate, int(int(model.gridPheromone.get_coord_attribute(coordinate))*mu))
                    else:
                        modelObject.gridPheromone.add_coord_attribute(coordinate, int(int(model.gridPheromone.get_coord_attribute(coordinate))*mu))

def EvaporatesDangerousPheromone(modelObject, stepCount, stepEvaporation, mu):
    if stepCount % stepEvaporation == 0:
        for i in range(modelObject.gridDangerousPheromone.width):
            for j in range(modelObject.gridDangerousPheromone.height):
                coordinate = (i,j)
                if(modelObject.gridDangerousPheromone.get_coord_attribute(coordinate) != 0 ):
                    if model.grid.get_coord_attribute((coordinate)) == 'Unflooded':
                        modelObject.gridDangerousPheromone.add_coord_attribute(coordinate, int(int(model.gridDangerousPheromone.get_coord_attribute(coordinate))*mu))
                    else:
                        modelObject.gridDangerousPheromone.add_coord_attribute(coordinate, int(int(model.gridDangerousPheromone.get_coord_attribute(coordinate))*mu))

def salvar_dataframe_para_csv(df, name_file):
    df.to_csv(name_file, index=False)




#################Initiate model #######################################
random.seed(2026)
for run_id in range(num_executions):
    print(f"\n### Running simulation #{run_id + 1}/{num_executions} ###\n")

    cont = 1
    days_to_run = int(sys.argv[1])
    clockDay = int(sys.argv[2])
    evaporation = int(sys.argv[3])
    mu = float(sys.argv[4])

    followers = int(sys.argv[5])
    explorers = int(sys.argv[6])

    plantsA = int(sys.argv[7])
    plantsB = int(sys.argv[8])
    plantsC = int(sys.argv[9])
    plantsD = int(sys.argv[10])

    nests = int(sys.argv[10])
    hyenas = int(sys.argv[11])
    crocodiles = int(sys.argv[12])

    model = HominidsModel(10, 10, path='MapsCsv/basicMapWaterHole100x100.csv', number_hominids_followers=followers, number_hominids_explorers = explorers, number_plantsA=plantsA, number_plantsB = plantsB, number_plantsC = plantsC, number_plantsD = plantsD, number_nests=nests, number_hyenas=hyenas, number_crocodiles=crocodiles)

    visualizationModel = Visualization(1280,720)

    visualizationModel.DrawPyGame(model, 0)

    listCarcass = []
    listPlants = []
    listHominids = []

    daily_calories = []
    daily_fruits = []
    daily_calories_need = []
    daily_attacks = []
    all_runs_total_calories = []
    max_attr_pheromone = []
    max_rep_pheromone = []
    all_runs_max_att_pheromone = []
    all_runs_max_rep_pheromone = []
    
    
    caloriesConsumedFollower = []
    caloriesConsumedExplorer = []

    caloriesCollectedFollower = []
    caloriesCollectedExplorer = []

    visitedCellsByExplorers = []
    visitedCellsByFollowers = []

    visitedCellsCollectingFoodByExplorers = []
    visitedCellsCollectingFoodByFollowers = []

    trajectoryByExplorer = []
    trajectoryByFollower = []


    trajectoryCollectingFoodByExplorer = []
    trajectoryCollectingFoodByFollower = []


    

    running = True
    space_press_count = 0
    for s in tqdm(range(clockDay * days_to_run)):

        if turn_on_visualization: # Turn on PyGame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_SPACE:  
                        space_press_count += 1
                        if space_press_count == 5: 
                            space_press_count = 0
                    
            if not running:
                break

        model.step()
        EvaporatesPheromone(model,s,evaporation, mu)
        EvaporatesDangerousPheromone(model,s,evaporation, mu)

        turn_on_visualization_heatmap = not turn_on_visualization_heatmap
        visualizationModel.DrawPyGame(model, space_press_count)


            
        if s%(clockDay-1) == 0:
            current_day = s // clockDay 
            print("Currently, it is day:", current_day)
            tcal = 0
            fruits = 0
            attacked = 0
            

            for a in model.schedule.agents:

                if a.agent_type in ["plantA", "plantB","plantC","plantD", "carcass"]:
                    tcal += a.available_calories

                if a.agent_type in ["plantA","plantB","plantC","plantD"]:
                    fruits += a.fruits
                    listPlants.append(a)

                if a.agent_type == "carcass":   
                    listCarcass.append(a)

                if a.agent_type == "hominid":
                    attacked += a.count_attack

                    
                    if a.hominin_type == "hominin_explorer":
                        
                        visitedCellsByExplorers.append(a.visited_cells)
                        trajectoryByExplorer.append({
                            "agent_id": a.unique_id,
                            "trajectory": a.trajectory
                        })

                        visitedCellsCollectingFoodByExplorers.append(a.visited_cells_gathering_food)
                        trajectoryCollectingFoodByExplorer.append({
                            "agent_id": a.unique_id,
                            "trajectory_gathering_food": a.trajectory_gathering_food
                        })

                        caloriesCollectedExplorer.append({
                            "agent_id": a.unique_id,
                            "collected_calories": a.total_collected_calories
                        })
                        
                    elif a.hominin_type == "hominin_follower":

                        visitedCellsByFollowers.append(a.visited_cells)
                        trajectoryByFollower.append({
                            "agent_id": a.unique_id,
                            "trajectory": a.trajectory
                        })

                        visitedCellsCollectingFoodByFollowers.append(a.visited_cells_gathering_food)
                        trajectoryCollectingFoodByFollower.append({
                            "agent_id": a.unique_id,
                            "trajectory_gathering_food": a.trajectory_gathering_food
                        })

                        caloriesCollectedFollower.append({
                            "agent_id": a.unique_id,
                            "collected_calories": a.total_collected_calories
                        })

            daily_calories.append(tcal)
    
            daily_fruits.append(fruits)

            daily_attacks.append(attacked)
            greatestA = max(model.max_attr_history)
            greatestR = max(model.max_rep_history)
            max_attr_pheromone.append(greatestA)
            max_rep_pheromone.append(greatestR)

    print("daily calories: ",daily_calories)
    

    
    pygame.quit()

      

    save_grid_as_csv(model.gridHeatMap, f"ResultsHeatMapsCsv/HeatMaps_run_{run_id + 1}.csv")
    save_grid_as_csv(model.gridHeatMapExplorers, f"ResultsHeatMapsCsv/Explorers/HeatMapsExplorers_run_{run_id + 1}.csv")
    save_grid_as_csv(model.gridHeatMapFollowers, f"ResultsHeatMapsCsv/Followers/HeatMapsFollowers_run_{run_id + 1}.csv")
    save_grid_as_csv(model.gridPheromone, f"PheromoneMap_run_{run_id + 1}.csv")
    save_grid_as_csv(model.gridDangerousPheromone, f"DangerousPheromoneMap_run_{run_id + 1}.csv")

    df_before = pd.DataFrame(model.calories_per_day)
    salvar_dataframe_para_csv(df_before, f"ResultsCaloriesCsv/Before_sharing_calories_per_day_per_hominins_run_{run_id + 1}.csv")

    df_before = pd.DataFrame(model.calories_explorers_per_day)
    salvar_dataframe_para_csv(df_before, f"ResultsCaloriesCsv/Explorers/Before_sharing_dailyCaloriesConsumedExplorers_run_{run_id + 1}.csv")

    df_before = pd.DataFrame(model.calories_followers_per_day)
    salvar_dataframe_para_csv(df_before, f"ResultsCaloriesCsv/Followers/Before_sharing_dailyCaloriesConsumedFollowers_run_{run_id + 1}.csv")

    df_after = pd.DataFrame(model.calories_per_day_after_sharing)
    salvar_dataframe_para_csv(df_after, f"ResultsCaloriesCsv/After_sharing_calories_per_day_per_hominins_run_{run_id + 1}.csv")

    df_after = pd.DataFrame(model.calories_aftersharing_explorers_per_day)
    salvar_dataframe_para_csv(df_after, f"ResultsCaloriesCsv/Explorers/After_sharing_dailyCaloriesConsumedExplorers_run_{run_id + 1}.csv")

    df_after = pd.DataFrame(model.calories_aftersharing_followers_per_day)
    salvar_dataframe_para_csv(df_after, f"ResultsCaloriesCsv/Followers/After_sharing_dailyCaloriesConsumedFollowers_run_{run_id + 1}.csv")

    df_dailycalories = pd.DataFrame({
        'sum_total_calories_per_day': model.sum_total_calories_per_day,
        'sum_total_calories_per_day_after_sharing': model.sum_total_calories_per_day_after_sharing
    })    


    df_dailycalories = pd.DataFrame({
    f"sum_total_calories_per_day_run_{run_id + 1}": model.sum_total_calories_per_day,
    })

    df_daily_fruits = pd.DataFrame(daily_fruits)
    salvar_dataframe_para_csv(df_dailycalories, f"ResultsCaloriesCsv/dailyCalories_per_day_run_{run_id + 1}.csv")
    salvar_dataframe_para_csv(df_daily_fruits, f"ResultsCaloriesCsv/dailyFruits_run_{run_id + 1}.csv")
    
    df_daily_attacks = pd.DataFrame(daily_attacks)
    salvar_dataframe_para_csv(df_daily_attacks, f"ResultsCaloriesCsv/dailyAttacks_run_{run_id + 1}.csv")


    trajectory_explorers_dict = {}

    for agent_data in trajectoryByExplorer:
        agent_id = agent_data["agent_id"]
        trajectory = agent_data["trajectory"]

        trajectory_explorers_dict[f"Explorer_{agent_id}"] = trajectory

    df_trajectory_explorers = pd.DataFrame(
        dict([
            (key, pd.Series(value))
            for key, value in trajectory_explorers_dict.items()
        ])
    )

    salvar_dataframe_para_csv(
        df_trajectory_explorers,
        f"ResultsTrajectoriesCsv/Explorers/trajectoryExplorers_run_{run_id + 1}.csv"
    )

    #### Explorers trajectory - Gathering food ######
    trajectory_gathering_food_explorers_dict = {}

    for agent_data in trajectoryCollectingFoodByExplorer:
        agent_id = agent_data["agent_id"]
        trajectory = agent_data["trajectory_gathering_food"]

        trajectory_gathering_food_explorers_dict[f"Explorer_{agent_id}"] = trajectory

    df_trajectory_gathering_food_explorers = pd.DataFrame(
        dict([
            (key, pd.Series(value))
            for key, value in trajectory_gathering_food_explorers_dict.items()
        ])
    )

    salvar_dataframe_para_csv(
        df_trajectory_gathering_food_explorers,
        f"ResultsTrajectoriesCsv/Explorers/trajectoryCollectingFoodExplorers_run_{run_id + 1}.csv"
    )

    trajectory_followers_dict = {}

    for agent_data in trajectoryByFollower:
        agent_id = agent_data["agent_id"]
        trajectory = agent_data["trajectory"]

        trajectory_followers_dict[f"Follower_{agent_id}"] = trajectory

    df_trajectory_followers = pd.DataFrame(
        dict([
            (key, pd.Series(value))
            for key, value in trajectory_followers_dict.items()
        ])
    )

    salvar_dataframe_para_csv(
        df_trajectory_followers,
        f"ResultsTrajectoriesCsv/Followers/trajectoryFollowers_run_{run_id + 1}.csv"
    )

    #### Followers trajectory - Gathering food ######
    trajectory_gathering_food_followers_dict = {}

    for agent_data in trajectoryCollectingFoodByFollower:
        agent_id = agent_data["agent_id"]
        trajectory = agent_data["trajectory_gathering_food"]

        trajectory_gathering_food_followers_dict[f"Follower_{agent_id}"] = trajectory

    df_trajectory_gathering_food_followers = pd.DataFrame(
        dict([
            (key, pd.Series(value))
            for key, value in trajectory_gathering_food_followers_dict.items()
        ])
    )

    salvar_dataframe_para_csv(
        df_trajectory_gathering_food_followers,
        f"ResultsTrajectoriesCsv/Followers/trajectoryCollectingFoodFollowers_run_{run_id + 1}.csv"
    )


    visited_cells_data = []

    for a in model.schedule.agents:

        if a.agent_type == "hominid":

            visited_cells_data.append({
                "run": run_id + 1,
                "agent_id": a.unique_id,
                "hominin_type": a.hominin_type,
                "unique_cells_visited": len(a.visited_cells)
            })

    df_visited_cells = pd.DataFrame(visited_cells_data)

    salvar_dataframe_para_csv(
        df_visited_cells,
        f"ResultsVisitedCells/uniqueVisitedCells_run_{run_id + 1}.csv"
    )

    visited_cells_collecting_food_data = []

    for a in model.schedule.agents:

        if a.agent_type == "hominid":

            visited_cells_collecting_food_data.append({
                "run": run_id + 1,
                "agent_id": a.unique_id,
                "hominin_type": a.hominin_type,
                "unique_cells_visited": len(a.visited_cells_gathering_food)
            })

    df_visited_cells_collecting = pd.DataFrame(visited_cells_collecting_food_data)

    salvar_dataframe_para_csv(
        df_visited_cells_collecting,
        f"ResultsVisitedCells/uniqueVisitedCellsCollectingFood_run_{run_id + 1}.csv"
    )

    collected_food_explorers_data = []

    for a in model.schedule.agents:

        if a.agent_type == "hominid":

            collected_food_explorers_data.append({
                "run": run_id + 1,
                "agent_id": a.unique_id,
                "hominin_type": a.hominin_type,
                "collected calories": a.total_collected_calories
            })

    df_collected_calories = pd.DataFrame(collected_food_explorers_data)

    salvar_dataframe_para_csv(
        df_collected_calories,
        f"ResultsCollectedFood/collectedFood_run_{run_id + 1}.csv"
    )


    pheromone_use_data = []

    for a in model.schedule.agents:

        if a.agent_type == 'hominid':
            pheromone_use_data.append({
                "run": run_id + 1,
                "agent_id": a.unique_id,
                "hominin_type": a.hominin_type,
                "total_moves": len(a.trajectory),
                "attr_memory_moves": a.attr_pheromone_guided_moves,
                "rep_memory_moves": a.rep_pheromone_guided_moves,
                "attractive_memory_deposits": a.pheromone_deposit_count,
                    
                })

    df_pheromone_use_data = pd.DataFrame(pheromone_use_data)
    
    salvar_dataframe_para_csv(
        df_pheromone_use_data,
        f"ResultsMemoryUseCsv/memoryUse_run_{run_id + 1}.csv"
    ) 

    df_daily_max_att_pheromone = pd.DataFrame(max_attr_pheromone)
    salvar_dataframe_para_csv(df_daily_max_att_pheromone, f"ResultsCaloriesCsv/dailyMaxAttrPheromone_run_{run_id + 1}.csv")
    df_daily_max_rep_pheromone = pd.DataFrame(max_rep_pheromone)
    salvar_dataframe_para_csv(df_daily_max_rep_pheromone, f"ResultsCaloriesCsv/dailyMaxRepPheromone_run_{run_id + 1}.csv")

    all_runs_calories.append(daily_calories)
    all_runs_fruits.append(daily_fruits)
    all_runs_attacks.append(daily_attacks)
    all_runs_total_calories.append(model.sum_total_calories_per_day)
    all_runs_max_att_pheromone.append(max_attr_pheromone)
    all_runs_max_rep_pheromone.append(max_rep_pheromone)

    print(f"End of simulation  #{run_id + 1}/{num_executions}")



    print("daily calories: ",daily_calories)
    print("daily fruits: ",daily_fruits)
    print("calories need: ",daily_calories_need)
    
df_calories = pd.DataFrame(all_runs_calories)
df_fruits = pd.DataFrame(all_runs_fruits)

df_all_runs_total_calories = pd.DataFrame(all_runs_total_calories)

df_all_runs_total_calories.to_csv("ResultsCaloriesCsv/teste.csv", index=False)
df_calories.to_csv("all_runs_calories.csv", index=False)
df_fruits.to_csv("all_runs_fruits.csv", index=False)


print("Simulations completed and data saved!")





 
      

