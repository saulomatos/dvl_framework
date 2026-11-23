import os  
import subprocess
import sys
import shutil
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', "tools"))
sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
    os.path.dirname(__file__), "..", "..", "..")), "tools"))
from sumolib import checkBinary  # noqa
import xml.etree.ElementTree as ET
import numpy as np
import time
import json

from reference_hv_generator import ReferenceHVGenerator

class Input:

    def __init__(self):
        if len(sys.argv) != 3: #not in (3, 4, 5): 
            exit("Parameters error.\n1) This script requires at least two parameters: scneario and flow")
        
        self.scenario = int(sys.argv[1])
        self.flow     =  sys.argv[2]
        # 1 e 2 com 10 medidas e os 3 fluxos
        # 3 moderado e intenso e fica faltando criar um baixo DOZE MEDIDAS
        # Cenário do SUMO
        #self.scenario = 1 #3 1 2 3
        #self.flow = 'baixo' #'baixo' 'moderado', 'intenso' criar fluxo baixo pro cenário 3

        if self.scenario in [1,2]:
            self.num_objectives = 10
        else:
            self.num_objectives = 12

        if self.num_objectives not in [6, 10, 12]:
            exit(f"num_objectives == {self.num_objectives} ... Not in 6, 10, 12")

        if self.flow not in ['baixo', 'moderado', 'intenso']:
            exit(f"flow == {self.flow} ... Not in 'baixo', 'moderado', 'intenso'")

        if self.num_objectives == 12 and self.scenario != 3:
            exit("num_objectives == 12 apenas para o cenário 3, por hora. E não é caso aqui")

        #self.num_variables = 8

        # Medidas utilizadas como objetivos
        '''
        self.objectives = [
            "departDelay",
            "duration",
            "waitingTime",
            "timeLoss",
            "CO2_abs",
            "fuel_abs"
        ]
        '''

        self.objectives = [
            "departDelay",
            "duration",
            "waitingCounting", #waitingTime",
            "timeLoss",
            "CO2_abs",
            "fuel_abs"
        ]

        if self.num_objectives >= 10:
            self.objectives.append("CO_abs")
            self.objectives.append("HC_abs")
            self.objectives.append("PMx_abs")
            self.objectives.append("NOx_abs")

        if self.num_objectives == 12:
            self.objectives.append("Global_mean_speed")
            self.objectives.append("Idle_time")

        # Número de execuções do experimento
        #self.num_execucoes = 1

        # Número de avaliações do algoritmo
        #self.num_avaliacoes = 2

        # Algoritmo de otimização
        self.algorithm = "NSGA2"

        self.lowerbound = 20
        self.upperbound = 120

        reference_path = './SUMO/cenario' + str(self.scenario) + '/' + self.flow + "/reference_point.json"

        #print(reference_path)

        if os.path.exists(reference_path):

            with open(reference_path, 'r', encoding='utf-8') as file:
                reference_data = json.load(file)

            #exit("leu jsomn")

            self.referenceHV = np.array([
                reference_data[objective] for objective in self.objectives
            ], dtype=float)

            '''
            old: 
            if False: #(self.scenario == 2 or self.scenario == 1) and self.flow == 'baixo':
                self.referenceHV = np.array([
                    17499854.51, 
                    2397784, 
                    1816123, 
                    2287134.57000001, 
                    11522710.3071638, 
                    4953205.11018303
                ], dtype=float)

            elif False: # self.scenario == 3 and self.flow == 'moderado':
                self.referenceHV = np.array([
                    80000000,
                    10000000,
                    8000000,
                    10000000,
                    30000000,
                    10000000
                ], dtype=float)
            '''
        else:
            #exit("oi")
            self.objective_values = []
            ReferenceHVGenerator(input=self)
            #print(self.objective_values)
            print("\n\n")
            with open(str(self.scenario) + '-' + self.flow + '.txt', 'w') as file:
                for k in range(len(self.objectives)):
                    print(f"{self.objectives[k]} = {self.objective_values[k]}")
                    file.write(f'{self.objectives[k]}=')
                    for j in self.objective_values[k]:
                        file.write(str(j) + ';')
                    file.write('\n')
            file.close()

            #print("\n1) json para input de -cenario; -fluxo; medidas;")
            #print("\n2) por fim, gerar pontos de referências para TODAS as medidas e deixar o código testado para 6, 8(?) 10(?) e 12 objetivos")
            #print(f"de volta ao input.py. Salvou os pontos de referências? Save as: scenario {self.scenario} and flow {self.flow}")
            exit("input.py, após ReferenceHVGenerator(self)")