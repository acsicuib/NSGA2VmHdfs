    #!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Copyright 2017 Carlos Guerrero, Isaac Lera.

Created on Wed Oct 16 08:12:04 2017
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

import copy
import random as random

class SYSTEMMODEL:
    
    def __init__(self):
        
        
        self.vmNumber = 0 #numero inicial/medio/fijo de virtual machines
        self.pmNumber = 0 #numero inicial/medio/fijo de pyshical machines
        self.blockNumber = 0 #numero inicial/medio/fijo de bloques
        self.replicationFactor = 0 #numero de replicas de cada bloque
        
        self.replicaNumber=0
        
        self.blockSize = 0
        
        self.resourceCPUUsageMultiplier = 0.0
        self.resourceIOUsageMultiplier = 0.0
        self.resourceNETUsageMultiplier = 0.0
        
    def TPDSmodel(self,populationSeed,vmSL,pmSL,fnSL):
        
        self.rnd = random.Random()
        self.rnd.seed(populationSeed)
        
        self.vmNumber=int(pmSL * vmSL) #initial number of vms in the system
        self.pmNumber=pmSL
        
        self.replicationFactor=3
        
        self.epsilomResourceWaste = 0.15
        
        
        self.replicaNumber=self.blockNumber * self.replicationFactor
        
        fileSizes = []
        fileAccess = []
        fileSizesTemplates = [1600, 1623, 1646, 1671, 1696, 1723, 1750, 1779, 1809, 1839, 1872, 1905, 1941, 1977, 2016, 2056, 2099, 2143, 2190, 2239, 2292, 2347, 2406, 2468, 2535, 2606, 2681, 2763, 2851, 2946, 3049, 3161, 3283, 3418, 3567, 3733, 3918, 4128, 4367, 4643, 4965, 5347, 5810, 6382, 7113, 8087, 9462, 11586, 15412, 25101]
        fileAccessTemplates =[125 ,77 ,57 ,47 ,40 ,35 ,31 ,29 ,26 ,24 ,23 ,21 ,20 ,19 ,18 ,17 ,17 ,16 ,15 ,15, 14 ,14 ,13 ,13 ,13 ,12 ,12 ,12 ,11 ,11, 11 ,10 ,10 ,10 ,10 ,10 ,9 ,9 ,9 ,9, 9 ,9 ,8 ,8 ,8 ,8 ,8 ,8 ,8 ,7]        

        j=0
        for i in range(0,fnSL):
            fileSizes.append(fileSizesTemplates[j])
            fileAccess.append(fileAccessTemplates[j])
            j +=1
            j = j % len(fileSizesTemplates)
            

        #transformamos los accesos a %
        
        totalAccess = float(sum(fileAccess))
        for i in range(len(fileAccess)):
            fileAccess[i] = float(fileAccess[i])/totalAccess
            
        #siempre ha de ser menor que los recursos de cpu disponibles
        self.resourceCPUUsageMultiplier = 0.1
        self.resourceIOUsageMultiplier =128
        self.resourceNETUsageMultiplier = 128

        

        self.blockSize = 64        
        #transformamos el tamaño de los ficheros a bloques
        for i in range(len(fileSizes)):
            fileSizes[i]=fileSizes[i]/self.blockSize
        
        
        
        self.blockLoad = [] 
        for i,v in enumerate(fileSizes):
            bcpu = fileAccess[i] * self.resourceCPUUsageMultiplier
            bio = fileAccess[i] * self.resourceIOUsageMultiplier * self.rnd.random()
            bnet = fileAccess[i] * self.resourceNETUsageMultiplier * self.rnd.random()
            for j in range(0,v):
                for k in range(0,self.replicationFactor):
                    self.blockLoad.append({"cpu" : bcpu, "io" : bio, "net" : bnet})
            
        self.blockNumber=sum(fileSizes)
        self.replicaNumber=len(self.blockLoad)

#******************************************************************************************
#   Variables modelo de energía de las máquinas
#******************************************************************************************
        
        self.pmTemplate = []
        self.pmTemplate.append({"name": "m0x", "cpu" : 24.0, "io" : 17800.0, "net" : 76800.0, "minfailrate": 0.15, "maxfailrate": 0.19, "energyLambda": 0.12, "energyAlpha": 5.29, "energyBeta": 0.68, "energyGamma": 0.05, "energyDelta": 0.1, "energyIdle": 501.0, "energyMax": 804.0})
        self.pmTemplate.append({"name": "0x", "cpu" : 12.0, "io" : 15000.0, "net" : 38400.0, "minfailrate": 0.3, "maxfailrate": 0.4, "energyLambda": 0.12, "energyAlpha": 4.33, "energyBeta": 0.47, "energyGamma": 0.05, "energyDelta": 0.1, "energyIdle": 164.0, "energyMax": 382.0})
           

        self.pmDefinition = []
        for i in range(0,self.pmNumber):
            self.pmDefinition.append(copy.deepcopy(self.pmTemplate[i%len(self.pmTemplate)]))


        self.vmTemplate = []
        self.vmTemplate.append({"name": "c3xlarge", "cpu" : 4.0, "io" : 250.0, "net" : 100.0, "minfailrate": 0.2, "maxfailrate": 2.5, })
        self.vmTemplate.append({"name": "c32xlarge", "cpu" : 8.0, "io" : 320.0, "net" : 240.0, "minfailrate": 0.4, "maxfailrate": 5.0,})
        self.vmTemplate.append({"name": "c34xlarge", "cpu" : 16.0, "io" : 400.0, "net" : 200.0, "minfailrate": 0.2, "maxfailrate": 2.5, })
        self.vmTemplate.append({"name": "m3xlarge", "cpu" : 4.0, "io" : 320.0, "net" : 100.0, "minfailrate": 0.4, "maxfailrate": 5.0,})
        self.vmTemplate.append({"name": "m32xlarge", "cpu" : 8.0, "io" : 400.0, "net" : 200.0, "minfailrate": 0.2, "maxfailrate": 2.5, })
                

        self.vmDefinition = []
        for i in range(0,self.vmNumber):
            self.vmDefinition.append(copy.deepcopy(self.vmTemplate[i%len(self.vmTemplate)]))

      
       
