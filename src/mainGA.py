    #!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Copyright 2017 Carlos Guerrero, Isaac Lera.

Created on Wed Oct 16 08:05:21 2017
@authors:
    Carlos Guerrero
    carlos ( dot ) guerrero  uib ( dot ) es
    Isaac Lera
    isaac ( dot ) lera  uib ( dot ) es


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.


This program has been implemented for the research presented in the
article "Multi-objective Optimization for Virtual Machine Allocation
and Replica Placement in Virtualized Hadoop Architecture" and 
submitted for evaluation to the "IEEE Transactions on Parallel and 
Distributed Systems" journal.
"""


import GA as ga
import SYSTEMMODEL as systemmodel
import pickle
from datetime import datetime
import os
import copy



#Setting of the directory where the results are stored
executionId= datetime.now().strftime('%Y%m%d%H%M%S')
file_path = "./"+executionId


if not os.path.exists(file_path):
    os.makedirs(file_path)

#Setting of the experiment sizes to be executed
vmScaleLevel = [2.0]
pmScaleLevel = [50,100,150,200]
fileNumberScaleLevel = [25,50,100,200]
#vmScaleLevel = [2.0]
#pmScaleLevel = [200]
#fileNumberScaleLevel = [200]

#Setting of the experiment scenarios to be executed
experimentList = []
# 0 - BOTH or VM or BLOCK
# 1 - NSGA2 or AIA
# 2 - lowScale, midScale or highScale
# 3 - mutation probability 0-1.0
# 4 - population size
# 5 - seed for random values for generation of the initial population
# 6 - seed for random values for evolution of populations
experimentList.append(['BOTH','NSGA2', 'TPDSmodel', 0.1,100,400,500])
experimentList.append(['VM','NSGA2', 'TPDSmodel', 0.1,100,400,500])
experimentList.append(['BLOCK','NSGA2', 'TPDSmodel', 0.1,100,400,500])
experimentList.append(['BLOCK','AIA', 'TPDSmodel', 0.95,100,400,500])



#Setting of the number of generations
numberofGenerations = 200

#Files to store sumarized results, comma-separated and point-separated
csvoutputSPA = open(file_path+'/agregatedResultsSPA.csv', 'w')
csvoutputUK = open(file_path+'/agregatedResultsUK.csv', 'w')


resultValues = "ex_number;scenario;algorithm;workload;vm;pm;filenumber;energy;resource;unavalaibility;wenergy;wresource;wunalvail;"
csvoutputUK.write(resultValues+'\n')
csvoutputUK.flush()
csvoutputSPA.write(resultValues.replace(".",",")+'\n')
csvoutputSPA.flush()


#Execution of the different experiment sizes and experiment scenarios previouly configured
for vmSL in vmScaleLevel:
    for pmSL in pmScaleLevel:
        for fnSL in fileNumberScaleLevel:
            

            for k,v in enumerate(experimentList):
                
                
                
                experimentName = str(v[:3])+"-vm"+str(vmSL)+"-pm"+str(pmSL)+"-fs"+str(fnSL)
                experimentName = experimentName.replace(",","-").replace(".","p").replace(" ","").replace("'","").replace("[","").replace("]","")
                experimentName = str(k)+"-"+experimentName
                print("*********************************") 
                print "*" + experimentName + " :::: "+ str(datetime.now())
                print("*********************************")
                #Creation of the system model
                system = systemmodel.SYSTEMMODEL()
            
            
                if v[2]=='TPDSmodel': system.TPDSmodel(v[5],vmSL,pmSL,fnSL)
                
                #Initialization of the Genetic Algorithm
                g = ga.GA(system,v[5],v[6])
                g.experimentScenario = v[0] # BOTH VM or BLOCK
                g.optimizationAlgorithm = v[1]
                g.mutationProbability = v[3]
                g.populationSize = v[4]
                
                #Initial population generation
                g.generatePopulation(g.populationPt)
                
                print "*** INITIAL POPULATION GENERATED ***"
                
                time=datetime.now()
                selectedSolution = []

                
                energy_weight= 1.0/3.0
                resourcewaste_weight= 1.0/3.0
                unavailability_weight= 1.0/3.0
                
                indexSelectedSolution = g.selectSolution(g.populationPt,energy_weight,resourcewaste_weight,unavailability_weight)   
                selectedSolution.append({"population": copy.deepcopy(g.populationPt.population[indexSelectedSolution]) ,"fitness": copy.deepcopy(g.populationPt.fitness[indexSelectedSolution]) ,"fitnessNormalized": copy.deepcopy(g.populationPt.fitnessNormalized[indexSelectedSolution]) ,"pmsUsages": copy.deepcopy(g.populationPt.pmsUsages[indexSelectedSolution]) ,"vmsUsages":  copy.deepcopy(g.populationPt.vmsUsages[indexSelectedSolution])  })
                
                
                #Evolution of the optimization algorithm along the consecutive generations till the max number of generations is achieved
                for i in range(0,numberofGenerations):
                    if g.optimizationAlgorithm == 'NSGA2':
                        g.evolveNSGA2()
                    if g.optimizationAlgorithm == 'AIA':
                        g.evolveAIA()
                    #Selection of the prefered solution to compare the results in the article
                    indexSelectedSolution = g.selectSolution(g.populationPt,energy_weight,resourcewaste_weight,unavailability_weight)   
                    selectedSolution.append({"population": copy.deepcopy(g.populationPt.population[indexSelectedSolution]) ,"fitness": copy.deepcopy(g.populationPt.fitness[indexSelectedSolution]) ,"fitnessNormalized": copy.deepcopy(g.populationPt.fitnessNormalized[indexSelectedSolution]) ,"pmsUsages": copy.deepcopy(g.populationPt.pmsUsages[indexSelectedSolution]) ,"vmsUsages":  copy.deepcopy(g.populationPt.vmsUsages[indexSelectedSolution])  })
                    timeold = time
                    time=datetime.now()
                    print "[Generation number "+str(i)+" of "+experimentName+"] "+ str(time-timeold)
                    
                    
                resultValues = str(k)+";"+str(v[0])+";"+str(v[1])+";"+str(v[2])+";"+str(vmSL)+";"+str(pmSL)+";"+str(fnSL)+";"+str(selectedSolution[-1]['fitness']['energy'])+";"+str(selectedSolution[-1]['fitness']['resourcewaste'])+";"+str(selectedSolution[-1]['fitness']['unavailability'])+";"+str(selectedSolution[-1]['fitnessNormalized']['energy'])+";"+str(selectedSolution[-1]['fitnessNormalized']['resourcewaste'])+";"+str(selectedSolution[-1]['fitnessNormalized']['unavailability'])
                csvoutputUK.write(resultValues+'\n')
                csvoutputUK.flush()
                csvoutputSPA.write(resultValues.replace(".",",")+'\n')
                csvoutputSPA.flush()                
                
                
            
                output = open(file_path+'/'+experimentName+'-lastGeneration.pkl', 'wb')
                pickle.dump(g.populationPt, output)
                output.close()
                
                output = open(file_path+'/'+experimentName+'-selectedSolution.pkl', 'wb')
                pickle.dump(selectedSolution, output)
                output.close()    
            
csvoutputUK.close()
csvoutputSPA.close()



