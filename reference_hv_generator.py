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
from datetime import datetime


class ReferenceHVGenerator():
    #print("oi, SUMOProblem")
    def __init__(self,
                scenario=1,
                config_file='config.sumocfg',
                output_file='tripinfos.xml',
                add_path='./SUMO/add_default.xml',
                input=None):

        self.scenario   = input.scenario
        self.flow        = input.flow
        self.scenario_path = './SUMO/cenario' + str(self.scenario) + '/' + self.flow
        if not os.path.isdir(self.scenario_path):  
            raise Exception("Scenario path doesn't exist!")      

        #print("oi, config")
        self.config_file = config_file
        print(f"self.config_file = {self.config_file}")
        self.config_path = self.scenario_path+'/'+self.config_file
        print(f"self.config_path = {self.config_path}")
        #exit("ea")
        if not os.path.isfile(self.config_path):  
            raise Exception("Config path file doesn't exist.")      

        self.output_file = output_file
        self.output_path = self.scenario_path+'/output/'+self.output_file
        self.add_path = add_path
        self.MAPA = self.scenario_path + "/net.xml"
        self.scenario_logics = []
        self.scenario_phases = []
        self.num_objectives = len(input.objectives)
        self.getPhasesTheirIdsAndTotal()
        self.objectives = input.objectives

        self.lowerbound  = input.lowerbound
        self.upperbound  = input.upperbound
        
        exit("ReferenceHVGenerator")
        print("Arthur é fluxo baixo para cenário 1 e 2, e fluxo moderado para cenário 3. E 6 (?) medidas\n")
        
        print("Cenário:", self.scenario)
        print("Fluxo:", self.flow)
        print("Objetivos:", self.objectives)
        print("Número de objetivos:", len(self.objectives))
        print("Número de variáveis de decisão:", self.num_variables)
        print(f"lower and upper bounds: [{self.lowerbound} .. {self.upperbound}]")
        print("Execuções: ONDE SETAREMOS ISSO DE FATO? na class Input?")#, input.num_execucoes)
        print("Avaliações: ONDE SETAREMOS ISSO DE FATO?  \"evaluations da class DVLFramework?")
        #, input.num_avaliacoes)
        print("Algoritmo: ONDE SETAREMOS ISSO DE FATO? na class Input?????")#, input.algorithm)
        #exit("e ae")

        #self.objectives = ["departDelay", "duration", "waitingCount", "timeLoss", "CO2_abs", "fuel_abs"]
        #medidas_trip = ["departDelay", "duration", "waitingCount", "timeLoss", "CO_abs", "CO2_abs", 
                    #"HC_abs", "PMx_abs", "NOx_abs", "fuel_abs", "vm_global"]#, "idle_time"] 

        for medida in self.objectives:
            setattr(self, medida, [float("-inf")] * 10)

        #print(self.objectives)

        self.obtainTenWorstResults()

        '''
        print(self.departDelay)
        print(self.duration)
        print(self.waitingTime)
        print(self.timeLoss)
        print(self.CO2_abs)
        print(self.fuel_abs)
        '''

        '''
        test_solution = np.random.randint(
            self.lowerbound,
            self.upperbound + 1,
            size=self.num_variables
        )

        #objectives = problem.evaluate([11, 20, 20, 13, 20, 20, 120, 20, 20, 40, 40, 20, 20, 20, 40, 40, 20, 20])
        test_out_objectives = self.evaluate(test_solution)

        print(f"test_out_objectives = {test_out_objectives}")

        self.updateWorstResults(test_out_objectives)

        print(self.departDelay)
        print(self.duration)
        print(self.waitingTime)
        print(self.timeLoss)
        print(self.CO2_abs)
        print(self.fuel_abs)
        exit("e ae") 
        '''

        
        '''
        print(self.departDelay)
        print(self.duration)
        print(self.waitingCounting) #print(self.waitingTime)
        print(self.timeLoss)
        print(self.CO2_abs)
        print(self.fuel_abs)
        '''

        input.objective_values.append(self.departDelay)
        input.objective_values.append(self.duration)
        input.objective_values.append(self.waitingCounting) # waitingTime
        input.objective_values.append(self.timeLoss)
        input.objective_values.append(self.CO2_abs)
        input.objective_values.append(self.fuel_abs)

        if self.num_objectives >= 10:
            '''
            print(self.CO_abs)
            print(self.HC_abs)
            print(self.PMx_abs)
            print(self.NOx_abs)
            '''

            input.objective_values.append(self.CO_abs)
            input.objective_values.append(self.HC_abs)
            input.objective_values.append(self.PMx_abs) 
            input.objective_values.append(self.NOx_abs)
            
        if self.num_objectives == 12:
            #print(self.Global_mean_speed)
            #print(self.Idle_time)

            input.objective_values.append(self.Global_mean_speed)
            input.objective_values.append(self.Idle_time)
             
            
    
    def obtainTenWorstResults(self):
        totalSimulations = 50 # 1000
        for i in range(totalSimulations): #range(1000):

            solution = np.random.randint(
                self.lowerbound,
                self.upperbound + 1,
                size=self.num_variables
            )

            objectives = self.evaluate(solution)

            self.updateWorstResults(objectives)
            
            #print(f"Simulation {i + 1} (of {totalSimulations}) concluded")
            if i % 10 == 0:
                print(f"Simulation {i + 1} (of {totalSimulations}) concluded at ", end='')
                now = datetime.now()
                print(now.strftime("%H:%M"))


    def updateWorstResults(self, objectives):

        for i, medida in enumerate(self.objectives):

            value = objectives[i]
            lista = getattr(self, medida)

            menor = min(lista)

            if value > menor:
                indice = lista.index(menor)
                lista[indice] = value

    def getPhasesTheirIdsAndTotal(self):
        numPhases = 0
        # self.MAPA         = dataDirectory + "Data/Mapas/"+str(mapa)+"/"+fluxo+"/net.xml"
        root = ET.parse(self.MAPA).getroot()
        for trafficLight in root.findall("./tlLogic"): # todos os semáforos
            numPhases += len([int(d.attrib['duration']) for d in trafficLight if 'G' in d.attrib['state'] or 'g' in d.attrib['state']])
            self.scenario_logics.append(trafficLight.attrib['id'])

        self.num_variables = numPhases

        for trafficLight in root.findall("./tlLogic")[0]:
            self.scenario_phases.append(trafficLight.attrib['state']) 

    def evaluate(self,
                    solutions=None):
        # transforming inputs
        #print("oi, evaluate")
        self.build_input_xml(solutions)
        # running simulation
        sumoBinary = checkBinary('sumo')                    
        retcode = subprocess.call(
            [sumoBinary, "-c", self.config_path, "--no-step-log", "--no-warnings"], stdout=open(os.devnull, "w"), stderr=sys.stderr)
        #stdout=sys.stdout,
        #stdout=open(os.devnull, "w")
        if retcode != 0:
            print(">> Simulation closed with status %s" % retcode)
        #sys.stdout.flush()
        # transforming outputs
        return self.parse_objectives()

    def build_input_xml(self, solutions=None):
        tree = ET.parse(self.add_path)
        root = tree.getroot()   

        i = 0

        for logic in self.scenario_logics:

            tlLogic = ET.SubElement(root, 'tlLogic')
            tlLogic.set('id', logic)
            tlLogic.set('type', 'static')
            tlLogic.set('programID', '1')
            tlLogic.set('offset', '0')

            for state in self.scenario_phases:

                phase = ET.SubElement(tlLogic, 'phase')
                phase.set('state', state)

                if 'G' in state or 'g' in state:
                    phase.set('duration', str(solutions[i]))
                    i += 1
                else:
                    phase.set('duration', '4')

        tree.write(self.scenario_path+'/'+'add.xml')

        #exit("e ae?????!")

    def parse_objectives(self):
        #print("oi, parse_objectives")
        tree = ET.parse(self.output_path)
        root = tree.getroot()     
        objectives = np.zeros(self.num_objectives)   
        numberOfTrips = 0
        vm_global     = 0
        fixed_duration = 18
        tam_rota = 749.9
        for tripinfo in root:
            numberOfTrips += 1
            objectives[0] += float(tripinfo.get('departDelay')) # ok
            objectives[1] += float(tripinfo.get('duration'))    # ok === trip duration
            #objectives[2] += float(tripinfo.get('waitingTime'))
            # vamos utilizar waitingCount (NÃO waitingTime) pois é igual a do mestrado que se chamava "wait steps" veja:
            # waitingTime	( s ) The time in which the vehicle speed was below or equal 0.1 m/s (scheduled stops do not count)
            # waitingCount	( #	) The number of times the vehicle speed went below or equal 0.1 m/s
            objectives[2] += int(tripinfo.get('waitingCount')) # ok === waitingCount
            #print(f"waitingCount {objectives[2]}")            
            objectives[3] += float(tripinfo.get('timeLoss'))   # ok
            for emission in tripinfo:      
                objectives[4] += float(emission.get('CO2_abs'))/1000   # ok
                objectives[5] += float(emission.get('fuel_abs'))/1000  # ok

                if self.num_objectives >= 10:
                    objectives[6] += float(emission.get('CO_abs'))/1000   # ok - Dividir por quanto
                    objectives[7] += float(emission.get('HC_abs'))/1000   # ok - Dividir por quanto
                    objectives[8] += float(emission.get('PMx_abs'))/1000  # ok - Dividir por quanto
                    objectives[9] += float(emission.get('NOx_abs'))/1000  # ok - Dividir por quanto

                if self.num_objectives == 12: 
                    if self.scenario != 3:
                        exit("num_objectives == 12 apenas para o cenário 3, por hora. E não é caso aqui")
                    
                    vm_global += tam_rota / float(tripinfo.get('duration')) # ok?? - E... Dividir por algo?
                    # Global mean speed: the sum of all average speeds divided by the number of vehicles
                    
                     # Isso tá ruim!!! 
                    objectives[11] += float(tripinfo.get('duration')) - fixed_duration # ok?? - E... Dividir por algo?
                    # Idle time: the duration of the trip minus the duration that the vehicle would take to make the trip without any stops
                    
        if self.num_objectives == 12 and self.scenario == 3:
            objectives[10] += (vm_global / numberOfTrips * -1) # Maximização
        # len(root.findall("./tripinfo")) * -1)           
        
        return objectives

    '''
    1. Depart delay, 2. Trip duration, 3. Wait steps, 4. Time loss, 5. CO abs, 6. CO2 abs, 7. HC abs, 8. PMx abs, 9. NOx abs, and 10. Fuel abs. 
    The remaining two measures (11-12) are obtained through calculations using the 2nd measure: 
    11. Global mean speed: the sum of all average speeds divided by the number of vehicles
    12. Idle time: the duration of the trip minus the duration that the vehicle would take to make the trip without any stops
    '''

    def referenceHV(self):
        exit(" def referenceHV(self) in sumoProblem.py") 
        #print("def referenceHV : setar os pontos de referencia? Estou usando 1 medida diferente, logo, 1 dos pontos tá errado. Ademais: apenas cenario 2?")
        #return self.referenceHV
        #np.array([17499854.51, 2397784, 1816123, 2287134.57000001, 11522710.3071638, 4953205.11018303])
    
    
