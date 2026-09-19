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


class SUMOProblem():
    #print("oi, SUMOProblem")
    def __init__(self,
                scenario=1,
                config_file='config.sumocfg',
                output_file='tripinfos.xml',
                add_path='./SUMO/add_default.xml',
                input=None):

        #print("oi, SUMOProblemaaaaaaaaaa")
        '''
        if input.scenario == 1:
            #print("oi, SUMOProblem = scen = 1111 ")
            self.scenario_path = './SUMO/cenario1'
            self.scenario_logics = ['2']
            self.scenario_phases = ['GGGrrrGGGrrr', 'yyyrrryyyrrr', 'rrrGGGrrrGGG', 'rrryyyrrryyy']
        elif input.scenario == 2:
            #print("oi, SUMOProblem = scen = 2222 ")
            self.scenario_path = './SUMO/cenario2'
            self.scenario_logics = ['1', '2', '3', '9']
            self.scenario_phases = ['GGGrrrGGGrrr', 'yyyrrryyyrrr', 'rrrGGGrrrGGG', 'rrryyyrrryyy']
            
        elif input.scenario == 3:
            self.scenario_path = './SUMO/cenario3'
            self.scenario_logics = ['10', '11', '14', '15', '16', '4', '5', '6', '9']
            self.scenario_phases = ['GGrrGGrr', 'yyrryyrr', 'rrGGrrGG', 'rryyrryy']
        else:
            raise Exception("Scenario doesn't exist!")
        '''

        self.scenario   = input.scenario
        self.scenario_path = './SUMO/cenario' + str(self.scenario)
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
        self.MAPA = self.scenario_path + "/net.xml"
        self.scenario_logics = []
        self.scenario_phases = []
        self.num_objectives = len(input.objectives)
        self.getPhasesTheirIdsAndTotal()
        self.objectives = input.objectives

        self.lowerbound  = input.lowerbound
        self.upperbound  = input.upperbound
        self.flow        = input.flow
        self.referenceHV = input.referenceHV
        
        print("Cenário:", self.scenario)
        print("Fluxo:", self.flow)
        print("Objetivos:", self.objectives)
        print("Número de objetivos:", len(self.objectives))
        print("Número de variáveis de decisão:", self.num_variables)
        print(f"lower and upper bounds: [{self.lowerbound} .. {self.upperbound}]")
        print("Execuções: ONDE SETAREMOS ISSO DE FATO? na class Input?")#, input.num_execucoes)
        print("Avaliações: ONDE SETAREMOS ISSO DE FATO?  \"evaluations da class DVLFramework?")
        #, input.num_avaliacoes)
        print("Algoritmo: ONDE SETAREMOS ISSO DE FATO? na class Input?")#, input.algorithm)
        #exit("e ae")

        #self.objectives = ["departDelay", "duration", "waitingCount", "timeLoss", "CO2_abs", "fuel_abs"]
        #medidas_trip = ["departDelay", "duration", "waitingCount", "timeLoss", "CO_abs", "CO2_abs", 
                    #"HC_abs", "PMx_abs", "NOx_abs", "fuel_abs", "vm_global"]#, "idle_time"] 
    
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
        exit(" def referenceHV(self) in sumoProblem.py") 
        #print("def referenceHV : setar os pontos de referencia? Estou usando 1 medida diferente, logo, 1 dos pontos tá errado. Ademais: apenas cenario 2?")
        #return self.referenceHV
        #np.array([17499854.51, 2397784, 1816123, 2287134.57000001, 11522710.3071638, 4953205.11018303])
    
    

#'''
if __name__ == "__main__":
    problem = SUMOProblem(scenario=2)
    process_start = time.process_time()
    clock_start = time.time()
    objectives = problem.evaluate([11, 20, 20, 13, 20, 20, 120, 20, 20, 40, 40, 20, 20, 20, 40, 40, 20, 20])
    print('Process Time {}'.format(time.process_time() - process_start))    
    print('Clock Time {}'.format(time.time() - clock_start))    
    print('Objectives {}'.format(objectives))    
#'''


'''
    def _build_input_xml(self, solutions=None):
        print("oi, build_input_xml")
        print(f"self.add_path = {self.add_path}")
        #exit("em build_input_xml")
        tree = ET.parse(self.add_path)
        root = tree.getroot()   
        
        for i,logic in enumerate(self.scenario_logics):
            #print(i, logic)
            tlLogic = ET.SubElement(root, 'tlLogic')
            tlLogic.set('id', logic) # função

            tlLogic.set('type', 'static') # SEMPRE!
            tlLogic.set('programID', '1') # SEMPRE Tem de ser '1' para não dar conflito com o net.xml
            tlLogic.set('offset', '0') # SEMPRE!

            phase1 = ET.SubElement(tlLogic, 'phase')
            phase1.set('duration', str(solutions[i*2]))  
            phase1.set('state', self.scenario_phases[0]) # função!
            
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

'''