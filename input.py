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

'''
class SUMOProblem():
    print("oi, SUMOProblem")
    def __init__(self,
                scenario=1,
                config_file='config.sumocfg',
                output_file='tripinfos.xml',
                add_path='./SUMO/add_default.xml'):

        #print("oi, SUMOProblemaaaaaaaaaa")
        if scenario == 1:
            #print("oi, SUMOProblem = scen = 1111 ")
            self.scenario_path = './SUMO/cenario1'
            self.scenario_logics = ['2']
            self.scenario_phases = ['GGGrrrGGGrrr', 'yyyrrryyyrrr', 'rrrGGGrrrGGG', 'rrryyyrrryyy']
        elif scenario == 2:
            #print("oi, SUMOProblem = scen = 2222 ")
            self.scenario_path = './SUMO/cenario2'
            self.scenario_logics = ['1', '2', '3', '9']
            self.scenario_phases = ['GGGrrrGGGrrr', 'yyyrrryyyrrr', 'rrrGGGrrrGGG', 'rrryyyrrryyy']
            
        elif scenario == 3:
            self.scenario_path = './SUMO/cenario3'
            self.scenario_logics = ['10', '11', '14', '15', '16', '4', '5', '6', '9']
            self.scenario_phases = ['GGrrGGrr', 'yyrryyrr', 'rrGGrrGG', 'rryyrryy']
        else:
            raise Exception("Scenario doesn't exist!")    
        if not os.path.isdir(self.scenario_path):  
            raise Exception("Scenario path doesn't exist!")      

        #print("oi, config")
        self.config_file = config_file
        self.config_path = self.scenario_path+'/'+self.config_file
        if not os.path.isfile(self.config_path):  
            raise Exception("Config path file doesn't exist.")      

        self.output_file = output_file
        self.output_path = self.scenario_path+'/output/'+self.output_file
        self.add_path = add_path
        self.num_objectives = 6
        self.num_variables = 8 # ele fez assim. Mas tem que ser extraído do net.xml

        self.medidas = ["departDelay", "duration", "waitingCount", "timeLoss", "CO2_abs", "fuel_abs"]
        #medidas_trip = ["departDelay", "duration", "waitingCount", "timeLoss", "CO_abs", "CO2_abs", 
                    #"HC_abs", "PMx_abs", "NOx_abs", "fuel_abs", "vm_global"]#, "idle_time"] 
        self.boo_trips = {"departDelay": False, "duration": False, "waitingCount": False, "timeLoss": False,
			     "CO_abs": False,      "CO2_abs": False,  "HC_abs": False,    "PMx_abs": False,
			     "NOx_abs": False,     "fuel_abs": False, "vm_global": False, "idle_time": False}
        
        self.setarMedidas()
    
    
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
        #print("oi, build_input_xml")
        tree = ET.parse(self.add_path)
        root = tree.getroot()   
        
        for i,logic in enumerate(self.scenario_logics):
            #print(i, logic)
            tlLogic = ET.SubElement(root, 'tlLogic')
            tlLogic.set('id', logic)
            tlLogic.set('type', 'static')
            tlLogic.set('programID', '1')
            tlLogic.set('offset', '0')

            phase1 = ET.SubElement(tlLogic, 'phase')
            phase1.set('duration', str(solutions[i*2]))
            phase1.set('state', self.scenario_phases[0])
            
            phase2 = ET.SubElement(tlLogic, 'phase')
            phase2.set('duration', '4')
            phase2.set('state', self.scenario_phases[1])
            
            phase3 = ET.SubElement(tlLogic, 'phase')
            phase3.set('duration', str(solutions[(i*2)+1]))
            phase3.set('state', self.scenario_phases[2])
            
            phase4 = ET.SubElement(tlLogic, 'phase')
            phase4.set('duration', '4')
            phase4.set('state', self.scenario_phases[3])

        tree.write(self.scenario_path+'/'+'add.xml')

    def parse_objectives(self):
        #print("oi, parse_objectives")
        tree = ET.parse(self.output_path)
        root = tree.getroot()     
        objectives = np.zeros(self.num_objectives)   
        for tripinfo in root:
            objectives[0] += float(tripinfo.get('departDelay'))
            objectives[1] += float(tripinfo.get('duration'))
            #não usamos waitingTime. E é bom que sejam as mesmas do meu mestrado pra poder comparar resultados
            objectives[2] += float(tripinfo.get('waitingTime'))
            #objectives[2] += int(tripinfo.get('waitingCount'))
            #print(f"waitingCount {objectives[2]}")            
            objectives[3] += float(tripinfo.get('timeLoss'))
            for emission in tripinfo:      
                objectives[4] += float(emission.get('CO2_abs'))/1000 
                objectives[5] += float(emission.get('fuel_abs'))/1000
                #objectives[5] += float(emission.get('fuel_abs'))

        return objectives

    def referenceHV(self):
        print("def referenceHV : setar os pontos de referencia? Estou usando 1 medida diferente, logo, 1 dos pontos tá errado. Ademais: apenas cenario 2?")
        return np.array([17499854.51, 2397784, 1816123, 2287134.57000001, 11522710.3071638, 4953205.11018303])
    
    def setarMedidas(self): #private void setarMedidas(String[] _medidas, int mapa){

        if "departDelay" in self.medidas:
            self.boo_trips["departDelay"] = True
        if "duration" in self.medidas:
            self.boo_trips["duration"] = True
        if "waitingCount" in self.medidas:
            self.boo_trips["waitingCount"] = True
        if "timeLoss" in self.medidas:
            self.boo_trips["timeLoss"] = True
        if"CO_abs" in self.medidas: 
            self.boo_trips["CO_abs"] = True
        if "CO2_abs" in self.medidas:
            self.boo_trips["CO2_abs"] = True
        if"HC_abs" in self.medidas:
            self.boo_trips["HC_abs"] = True
        if "PMx_abs" in self.medidas:
            self.boo_trips["PMx_abs"] = True
        if "NOx_abs" in self.medidas:
            self.boo_trips["NOx_abs"] = True
        if "fuel_abs" in self.medidas:
            self.boo_trips["fuel_abs"] = True
        if "vm_global" in self.medidas:
            self.boo_trips["vm_global"] = True

        if "idle_time" in self.medidas:
            if (self.scenario != 3):
                exit("Não foi escolhido o Cenário 03 Moderado, sendo que a medida Idle Time foi escolhida.\nPor hora ela só funciona no Cenário 03, pois necessita do cálculo da duração ideal.\nSendo assim, essa medida não será utilizada no Algoritmo") 
            else:
                self.boo_trips["idle_time"] = True
'''

class Input:

    def __init__(self):

        # Cenário do SUMO
        self.scenario = 3 #1 2 3
        self.flow = ''

        print('''\nresolver pontos de referência cenário 3 e depois para todos os cenários e fluxos.\n
        resolver executar com diversos objetivos e seus respectivos pontos de referências\n
        resolver isso tudo para diferentes fluxos\n
        ter como entrada estes diversos parâmetros por meio de arquivo json''')

        #self.num_variables = 8

        # Medidas utilizadas como objetivos
        self.objectives = [
            "departDelay",
            "duration",
            "waitingTime",
            "timeLoss",
            "CO2_abs",
            "fuel_abs"
        ]

        # Número de execuções do experimento
        #self.num_execucoes = 1

        # Número de avaliações do algoritmo
        #self.num_avaliacoes = 2

        # Algoritmo de otimização
        self.algorithm = "NSGA2"

        self.lowerbound = 20
        self.upperbound = 120

        if self.scenario == 2 or self.scenario == 1:
            self.referenceHV = np.array([
                17499854.51, 
                2397784, 
                1816123, 
                2287134.57000001, 
                11522710.3071638, 
                4953205.11018303
            ])

        elif self.scenario == 3:
            self.referenceHV = np.array([
                80000000,
                10000000,
                8000000,
                10000000,
                30000000,
                10000000
            ])

        '''
        self.boo_trips = {"departDelay": False, "duration": False, "waitingCount": False, "timeLoss": False,
                         "CO_abs": False,      "CO2_abs": False,  "HC_abs": False,    "PMx_abs": False,
                         "NOx_abs": False,     "fuel_abs": False, "vm_global": False, "idle_time": False}
                
                self.setarMedidas()
        
        def setarMedidas(self): #private void setarMedidas(String[] _medidas, int mapa){
        
                if "departDelay" in self.medidas:
                    self.boo_trips["departDelay"] = True
                if "duration" in self.medidas:
                    self.boo_trips["duration"] = True
                if "waitingCount" in self.medidas:
                    self.boo_trips["waitingCount"] = True
                if "timeLoss" in self.medidas:
                    self.boo_trips["timeLoss"] = True
                if"CO_abs" in self.medidas: 
                    self.boo_trips["CO_abs"] = True
                if "CO2_abs" in self.medidas:
                    self.boo_trips["CO2_abs"] = True
                if"HC_abs" in self.medidas:
                    self.boo_trips["HC_abs"] = True
                if "PMx_abs" in self.medidas:
                    self.boo_trips["PMx_abs"] = True
                if "NOx_abs" in self.medidas:
                    self.boo_trips["NOx_abs"] = True
                if "fuel_abs" in self.medidas:
                    self.boo_trips["fuel_abs"] = True
                if "vm_global" in self.medidas:
                    self.boo_trips["vm_global"] = True
        
                if "idle_time" in self.medidas:
                    if (self.scenario != 3):
                        exit("Não foi escolhido o Cenário 03 Moderado, sendo que a medida Idle Time foi escolhida.\nPor hora ela só funciona no Cenário 03, pois necessita do cálculo da duração ideal.\nSendo assim, essa medida não será utilizada no Algoritmo") 
                    else:
                        self.boo_trips["idle_time"] = True
        '''

'''
problem = SUMOProblem(scenario=2)
process_start = time.process_time()
clock_start = time.time()
objectives = problem.evaluate([11, 20, 20, 13, 20, 20, 120, 20, 20, 40, 40, 20, 20, 20, 40, 40, 20, 20])
print('Process Time {}'.format(time.process_time() - process_start))    
print('Clock Time {}'.format(time.time() - clock_start))    
print('Objectives {}'.format(objectives))    
'''

