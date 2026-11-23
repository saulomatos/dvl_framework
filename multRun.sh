#! /bin/sh

#date
#python3 real_optimization_experiment.py 1 baixo
#date
#python3 real_optimization_experiment.py 1 moderado
#date
#python3 real_optimization_experiment.py 1 intenso
#date
#python3 real_optimization_experiment.py 2 baixo
#date
#python3 real_optimization_experiment.py 2 moderado
#date
#python3 real_optimization_experiment.py 2 intenso
date
python3 real_optimization_experiment.py 3 moderado
date
python3 real_optimization_experiment.py 3 intenso


Segue a tabela consolidada dos três cenários, considerando a quantidade de medidas com pelo menos um possível valor extremo pelo critério IQR (1,5 × IQR).

| Cenário 	| Fluxo baixo | Fluxo moderado | Fluxo intenso |
|
| **Cenário 1** | **4/10**    | **1/10** | **0/10** |
| **Cenário 2** | **3/10**    | **3/10** | **0/10** |
| **Cenário 3** | —           | **9/12** | **8/12** |


The parameters used in NSGA-III were deined by the pymoo (Blank; Deb, 2020), which is a python framework for optimization. For the simulated binary crossover (DEB; AGRAWAL et al., 1995), the distribution index is set to ηc = 30, and the crossover probability pc = 1.0. For the polynomial mutation (DEB; GOYAL, 1996), the distribution index and the mutation probability are set to ηm = 20 and pm = 1/n, respectively, as recommended in (DEB, 2001). The population size used was 91 and 220 for the problem with « and 10 objectives, respectively, and the individual has a length of 12 for both objective sizes.


