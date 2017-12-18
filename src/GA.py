    #!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Copyright 2017 Carlos Guerrero, Isaac Lera.

Created on Wed Oct 16 08:04:42 2017
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


import numpy as np
import random as random
import sys
import POPULATION as pop
import matplotlib.pyplot as plt3d
import SYSTEMMODEL as systemmodel
import copy
from datetime import datetime



class GA:
    """
    Implementation of the optimization algorithm
    Args:
        system (SYSTEMMODEL instance): The modeling of the system.
        populationSeed (int): seed for the random serie for the population creation
        evolutionSeed (int): seed for the random serie for the evolution of the populaiton


    """    
    
    
    def __init__(self, system, populationSeed,evolutionSeed):
        
        
        
        self.system = system
        
        self.populationSize = 100
        self.populationPt = pop.POPULATION(self.populationSize)
        self.mutationProbability = 0.25

        self.rndPOP = random.Random()
        self.rndEVOL = random.Random()
        
        self.rndPOP.seed(populationSeed)
        self.rndEVOL.seed(evolutionSeed)
        
        
        self.optimizationAlgorithm = 'NSGA2' # NSGA2 or AIA
        self.experimentScenario = 'BOTH' # BOTH VM or BLOCK
        self.printTimes = True


    def selectSolution(self, population, ew, rw, uw):
        """
        Select a solution from the pareto optimal set by applying a weighted-sum transformation
        Args:
            ew (float): weigth for the power consumption objective
            rw (float): weigth for the resource waste objective
            uw (float): weigth for the file unavailability objective
        Returns:
            the index of the solution with the smallest weighted-sum value
        """ 
        
        energy = []
        resourcewaste = []
        unavailability = []
        for i in range(0,len(population.fitness)):
            energy.append(population.fitness[i]['energy'])
            resourcewaste.append(population.fitness[i]['resourcewaste'])
            unavailability.append(population.fitness[i]['unavailability'])
            
        minenergy = min(energy)
        minresourcewaste = min(resourcewaste)
        minunavailability = min(unavailability)
        
        diffenergy = max(energy) - minenergy
        diffresourcewaste = max(resourcewaste) - minresourcewaste
        diffunavailability = max(unavailability) - minunavailability

        
        fitness = []
        
        for i,v in enumerate(energy):
        
            if diffenergy == float('inf'):
                energyValue = 1.0*(ew)
            else:
                if (diffenergy) > 0:
                    energyValue = (ew) * ((energy[i]-minenergy)/diffenergy)
                else:
                    energyValue = energy[i]
            
            if diffresourcewaste == float('inf'):
                resourcewasteValue = 1.0*(rw)
            else:            
                if (diffresourcewaste) > 0:
                    resourcewasteValue = (rw) * ((resourcewaste[i]-minresourcewaste)/diffresourcewaste)
                else:
                    resourcewasteValue = resourcewaste[i]


            if diffunavailability == float('inf'):
                unavailabilityValue = 1.0*(uw)
            else:            
                if (diffunavailability) > 0:
                    unavailabilityValue = (uw) * ((unavailability[i]-minunavailability)/diffunavailability)
                else:
                    unavailabilityValue = unavailability[i]

            
            population.fitnessNormalized[i]={'energy': energyValue, 'resourcewaste': resourcewasteValue, 'unavailability': unavailabilityValue, 'fitness': energyValue+resourcewasteValue+unavailabilityValue}
            fitness.append(energyValue+resourcewasteValue+unavailabilityValue)
            
            
        minfitness = min(fitness)
        
        return fitness.index(minfitness)
                
            



#******************************************************************************************
#   MUTATIONS
#******************************************************************************************


    def VmGrowth(self,child):
        """
        Mutation operator that increases the number of VM in the vm-chromosome
        Args:
            child (dictionay): individual to be mutated
        """
        
        child['vm'].append(self.rndEVOL.randint(0,self.system.pmNumber-1))
        child['vmtype'].append(self.rndEVOL.randint(0,len(self.system.vmTemplate)-1))
        child['block'][self.rndEVOL.randint(0,len(child['block'])-1)] = len(child['vm'])-1        


        
    def VmShrink(self,child):
        """
        Mutation operator that decreases the number of VM in the vm-chromosome
        Args:
            child (dictionay): individual to be mutated
        """

        vm_i = self.rndEVOL.randint(0,len(child['vm'])-1)
        del child['vm'][vm_i]
        del child['vmtype'][vm_i]
        
        for i,v in enumerate(child['block']):
            if v == vm_i:
                
                replicasetId = i / self.system.replicationFactor
                replicasetIni = replicasetId * self.system.replicationFactor
                replicasetEnd = replicasetIni + self.system.replicationFactor
                replicaset = set(child['block'][replicasetIni:replicasetEnd])
                newvm = self.rndEVOL.randint(0,len(child['vm'])-1)
                triesLimit = 0
                while (newvm in replicaset) and (triesLimit<len(child['vm'])*2):
                    triesLimit +=1
                    newvm = self.rndEVOL.randint(0,len(child['vm'])-1)
                child['block'][i] = newvm
            elif v>vm_i:
                child['block'][i] -= 1
          
           
        

    def VmReplace(self,child):
        """
        Mutation operator that changes the allocation of VM in the vm-chromosome
        Args:
            child (dictionay): individual to be mutated
        """
        
        for vm_i in range(0,len(child['vm'])):
            if self.rndEVOL.random()>0.5:
                child['vm'][vm_i] = self.rndEVOL.randint(0,self.system.pmNumber-1)
        self.removeEmptyVms(child)


    def BlockReplace(self,child):
        """
        Mutation operator that changes the placement of the replicas in the block-chromosome
        Args:
            child (dictionay): individual to be mutated
        """
        
        for block_i in range(0, (len(child['block'])/self.system.replicationFactor)):
            if self.rndEVOL.random() > 0.5:
                vm_is = self.rndEVOL.sample(xrange(0,len(child['vm'])),self.system.replicationFactor)      
                for i in range(0,self.system.replicationFactor):
                    child['block'][(block_i*self.system.replicationFactor)+i] = vm_is[i]                     
        self.removeEmptyVms(child)


    
    def mutateBlock(self,child):
        """
        Block mutation of a solution by applying the unique block mutation operator
        Args:
            child (dictionay): individual to be mutated
        """
        
        mutationOperators = [] 
        mutationOperators.append(self.BlockReplace)
        mutationOperators[self.rndEVOL.randint(0,len(mutationOperators)-1)](child)

        
    def mutateVm(self,child):
        """
        VM mutation of a solution by selecting one of the three available vm mutation operator
        Args:
            child (dictionay): individual to be mutated
        """

        mutationOperators = [] 
        modifyNumberRnd = self.rndEVOL.random()
        if (modifyNumberRnd < 1./3.):
            self.VmGrowth(child)
        if (modifyNumberRnd > 1./3.):
            self.VmShrink(child)
        mutationOperators.append(self.VmReplace)

        mutationOperators[self.rndEVOL.randint(0,len(mutationOperators)-1)](child)
    
                
    def mutate(self,child):
        """
        Selection of the type of mutations to be applyed depending on the experiment scenario
        Args:
            child (dictionay): individual to be mutated
        """
                       
#        self.mutateVm(child)
#        self.mutateBlock(child)      

        if self.experimentScenario=='BOTH':
            self.mutateVm(child)
            self.mutateBlock(child)  
        
        if self.experimentScenario=='VM':
            self.mutateVm(child)
        
        if self.experimentScenario=='BLOCK':
            self.mutateBlock(child)

        
        
        
        

#******************************************************************************************
#   END MUTATIONS
#******************************************************************************************


#******************************************************************************************
#   CROSSOVER
#******************************************************************************************



    def crossoverBOTHBlock(self,f1,f2,offs):
        """
        Second phase of the one-point crossover operator for the experiment scenario NSGA-both
        Args:
            f1 (list of dictionaries): chromosomes of the first father
            f2 (list of dictionaries): chromosomes of the second father
            offs (populaiton instance): solutions in the offspring
        Returns:
            The two new children generarted from f1 and f2
        """
        
        #c1 = copy.deepcopy(f1)
        #c2 = copy.deepcopy(f2)
        
        c1={}
        c2={}
        
        c1['vm']=[]
        c1['vmtype']=[]
        c1['block']=[]

        c2['vm']=[]
        c2['vmtype']=[]
        c2['block']=[]
        
        
        cuttingPoint = self.rndEVOL.randint(1,len(f1['block'])-1)
        

        

            
        #create the vm-chromosomes from the joining of both complete vm-chromosomes of the fathers
        
        newvmCh1 = f1['vm'] + f2['vm']
        newvmCh2 = f1['vm'] + f2['vm']
        
        newvmtypeCh1 = f1['vmtype'] + f2['vmtype']
        newvmtypeCh2 = f1['vmtype'] + f2['vmtype']
        
        #apply one-point cutting point to the block-chromosome

        newblockCh1 = f1['block'][:cuttingPoint] + f2['block'][cuttingPoint:]
        newblockCh2 = f2['block'][:cuttingPoint] + f1['block'][cuttingPoint:]
        
        
        
        #rename all the vms of the second father/child
        shiftVm4c2 = len(f1['vm'])
        
        for i in range(cuttingPoint,len(f2['block'])):
            newblockCh1[i] += shiftVm4c2

        for i in range(0,cuttingPoint):
            newblockCh2[i] += shiftVm4c2
         
        

        c1['vm'] = newvmCh1      
        c2['vm'] = newvmCh2      

        c1['vmtype'] = newvmtypeCh1      
        c2['vmtype'] = newvmtypeCh2      


        c1['block'] = newblockCh1      
        c2['block'] = newblockCh2      
            
        
        self.removeEmptyVms(c1)
        self.removeEmptyVms(c2)


        offs.append(c1)
        offs.append(c2)

        return c1,c2

    def crossoverVMandType(self,f1,f2,offs):
        
        """
        One-point crossover operator for the experiment scenario NSGA-vm
        Args:
            f1 (list of dictionaries): chromosomes of the first father
            f2 (list of dictionaries): chromosomes of the second father
            offs (populaiton instance): solutions in the offspring
        Returns:
            The two new children generarted from f1 and f2
        """

        #c1 = copy.deepcopy(f1)
        #c2 = copy.deepcopy(f2)
        c1={}
        c2={}
        
        c1['vm']=[]
        c1['vmtype']=[]
        c1['block']=[]

        c2['vm']=[]
        c2['vmtype']=[]
        c2['block']=[]
        
        cuttingPoint = self.rndEVOL.randint(1,min(len(f1['vm']),len(f2['vm']))-1)
        cuttingPoint2 = self.rndEVOL.randint(1,min(len(f1['vm']),len(f2['vm']))-1)
        
        newvmCh1 = f1['vm'][:cuttingPoint] + f2['vm'][cuttingPoint:]
        newvmCh2 = f2['vm'][:cuttingPoint] + f1['vm'][cuttingPoint:]
        

        c1['vm'] = newvmCh1      
        c2['vm'] = newvmCh2      

        newvmtypeCh1 = f1['vmtype'][:cuttingPoint2] + f2['vmtype'][cuttingPoint2:]
        newvmtypeCh2 = f2['vmtype'][:cuttingPoint2] + f1['vmtype'][cuttingPoint2:]
        

        c1['vmtype'] = newvmtypeCh1      
        c2['vmtype'] = newvmtypeCh2
        
        
        #we distribute the blocks in the vms in a roundrobin strategy
        c1['block'] = self.generateRoundRobin1D(self.system.replicaNumber,len(c1['vm']))
        c2['block'] = self.generateRoundRobin1D(self.system.replicaNumber,len(c2['vm']))
        
        

        offs.append(c1)
        offs.append(c2)

        return c1,c2
        
    def crossoverBOTHVMandType(self,f1,f2,offs):
        
        """
        First phase of the one-point crossover operator for the experiment scenario NSGA-both
        Args:
            f1 (list of dictionaries): chromosomes of the first father
            f2 (list of dictionaries): chromosomes of the second father
            offs (populaiton instance): solutions in the offspring
        Returns:
            The two new children generarted from f1 and f2
        """

        #c1 = copy.deepcopy(f1)
        #c2 = copy.deepcopy(f2)
        
        c1={}
        c2={}
        
        c1['vm']=[]
        c1['vmtype']=[]
        c1['block']=[]

        c2['vm']=[]
        c2['vmtype']=[]
        c2['block']=[]
        
        cuttingPoint = self.rndEVOL.randint(1,min(len(f1['vm']),len(f2['vm']))-1)
        cuttingPoint2 = self.rndEVOL.randint(1,min(len(f1['vm']),len(f2['vm']))-1)
        
        newvmCh1 = f2['vm'][:cuttingPoint] + f1['vm'][cuttingPoint:]
        newvmCh2 = f1['vm'][:cuttingPoint] + f2['vm'][cuttingPoint:]
        

        c1['vm'] = newvmCh1      
        c2['vm'] = newvmCh2      

        newvmtypeCh1 = f2['vmtype'][:cuttingPoint2] + f1['vmtype'][cuttingPoint2:]
        newvmtypeCh2 = f1['vmtype'][:cuttingPoint2] + f2['vmtype'][cuttingPoint2:]
        

        c1['vmtype'] = newvmtypeCh1      
        c2['vmtype'] = newvmtypeCh2
        
        c1['block']=copy.copy(f1['block'])
        c2['block']=copy.copy(f2['block'])

        offs.append(c1)
        offs.append(c2)

        return c1,c2
        

        
        
    def crossoverBLOCK(self,f1,f2,offs):
        
        """
        One-point crossover operator for the experiment scenario NSGA-block
        Args:
            f1 (list of dictionaries): chromosomes of the first father
            f2 (list of dictionaries): chromosomes of the second father
            offs (populaiton instance): solutions in the offspring
        Returns:
            The two new children generarted from f1 and f2
        """

        #c1 = copy.deepcopy(f1)
        #c2 = copy.deepcopy(f2)
        
        
        c1={}
        c2={}
        
        c1['vm']=[]
        c1['vmtype']=[]
        c1['block']=[]

        c2['vm']=[]
        c2['vmtype']=[]
        c2['block']=[]
        
        cuttingPoint = self.rndEVOL.randint(1,len(f1['block'])-1)
        
        
        #apply one-point cutting point to the block-chromosome

        newblockCh1 = f1['block'][:cuttingPoint] + f2['block'][cuttingPoint:]
        newblockCh2 = f2['block'][:cuttingPoint] + f1['block'][cuttingPoint:]
        

        c1['block'] = newblockCh1      
        c2['block'] = newblockCh2     
        
        c1['vmtype']=copy.copy(f1['vmtype'])
        c2['vmtype']=copy.copy(f2['vmtype'])
        
        c1['vm']=copy.copy(f1['vm'])
        c2['vm']=copy.copy(f2['vm'])
            

        offs.append(c1)
        offs.append(c2)

        return c1,c2
        
        
        
    def crossover(self,f1,f2,offs):
        
        """
        Function that determines which are the crossover operators to applied
        depending on the experiment scenario scope.
        Args:
            f1 (list of dictionaries): chromosomes of the first father
            f2 (list of dictionaries): chromosomes of the second father
            offs (populaiton instance): solutions in the offspring
        """
        
        if self.experimentScenario=='BOTH':
            c1,c2 = self.crossoverBOTHVMandType(f1,f2,offs)
            self.crossoverBOTHBlock(c1,c2,offs)      

        if self.experimentScenario=='VM':
            self.crossoverVMandType(f1,f2,offs)

        if self.experimentScenario=='BLOCK':
            self.crossoverBLOCK(f1,f2,offs)




#******************************************************************************************
#   END CROSSOVER
#******************************************************************************************




#******************************************************************************************
#   Node Workload calculation
#******************************************************************************************

    def calculateVmsWorkload(self, solution):

        """
        Calculates the workload generated over all the VMs considering the VM and replica
        distribution in the variable solution.
        Args:
            solution (list of dictionaries): chromosomes of the solution
        """        
        
        vmsLoad = {}
        vmsLoad['cpu']=[]
        vmsLoad['io']=[]
        vmsLoad['net']=[]
        
        
        for vm_i in range(0,len(solution['vm'])):
            vmsLoad['cpu'].append(0.0)
            vmsLoad['io'].append(0.0)
            vmsLoad['net'].append(0.0)
            
        for block_i in range(0,len(solution['block'])):
            vmsLoad['cpu'][solution['block'][block_i]] += self.system.blockLoad[block_i]['cpu']
            vmsLoad['io'][solution['block'][block_i]] += self.system.blockLoad[block_i]['io']
            vmsLoad['net'][solution['block'][block_i]] += self.system.blockLoad[block_i]['net']

        return vmsLoad
        
    def calculatePmsWorkload(self, solution, vmsLoad):
        """
        Calculates the workload generated over all the PMs considering the VM and replica
        distribution in the variable solution.
        Args:
            solution (list of dictionaries): chromosomes of the solution
            vmsLoad (list of dictionaries): VMs usages for the current solution
        """         
        pmsLoad = {}
        pmsLoad['cpu']=[]
        pmsLoad['io']=[]
        pmsLoad['net']=[]
        
        
        for pm_i in range(0,self.system.pmNumber):
            pmsLoad['cpu'].append(0.0)
            pmsLoad['io'].append(0.0)
            pmsLoad['net'].append(0.0)
            

        for vm_i in range(0,len(solution['vm'])):
            pmsLoad['cpu'][solution['vm'][vm_i]] += vmsLoad['cpu'][vm_i]
            pmsLoad['io'][solution['vm'][vm_i]] += vmsLoad['io'][vm_i]
            pmsLoad['net'][solution['vm'][vm_i]] += vmsLoad['net'][vm_i]
            
        return pmsLoad
        
        
        
    def calculateSolutionsWorkload(self,pop):
        """
        Calculates the workload generated over the VMs and the PMs for all the
        solutions in the populaiton.
        Args:
            pop (populaiton instances): solution population
        """ 
        
        for i,citizen in enumerate(pop.population):
            pop.vmsUsages[i]=self.calculateVmsWorkload(citizen)
            pop.pmsUsages[i]=self.calculatePmsWorkload(citizen,pop.vmsUsages[i])
        

#******************************************************************************************
#   END Node Workload calculation
#******************************************************************************************


#******************************************************************************************
#   Model constraints
#******************************************************************************************

    
    def resourceUsages(self,pop,index):
        """
        Checks the violation of either the PM or VM constraints.
        Args:
            pop (populaiton instances): solution population
            index (int): index of the solution to check
        Return:
            True/False: if the constraint is violated (False) or not (True)
        """ 

#checking pm has less resources usages than their templates

        for pm_i in range(0,self.system.pmNumber):
            
            pmtemplate = self.system.pmDefinition[pm_i]
            
            if pmtemplate['cpu']<pop.pmsUsages[index]['cpu'][pm_i]:
#                print "CPU usage constraint not satified for solution "+str(index)+ " and PM "+str(pm_i)
#                print "template value "+str(pmtemplate['cpu']) + " and usage value "+str(pop.pmsUsages[index]['cpu'][pm_i])
                return False

            if pmtemplate['net']<pop.pmsUsages[index]['net'][pm_i]:
#                print "NET usage constraint not satified for solution "+str(index)+ " and PM "+str(pm_i)
#                print "template value "+str(pmtemplate['net']) + " and usage value "+str(pop.pmsUsages[index]['net'][pm_i])
                return False

            if pmtemplate['io']<pop.pmsUsages[index]['io'][pm_i]:
#                print "IO usage constraint not satified for solution "+str(index)+ " and PM "+str(pm_i)
#                print "template value "+str(pmtemplate['io']) + " and usage value "+str(pop.pmsUsages[index]['io'][pm_i])
                return False



        
        
#checking vm has less resource usages than their templates        
 
        for vm_i in range(0,len(pop.population[index]['vmtype'])):
            
            vmtemplate = self.system.vmTemplate[pop.population[index]['vmtype'][vm_i]]
            
            if vmtemplate['cpu']<pop.vmsUsages[index]['cpu'][vm_i]:
#                print "CPU usage constraint not satified for solution "+str(index)+ " and VM "+str(vm_i)
#                print "template value "+str(vmtemplate['cpu']) + " and usage value "+str(pop.vmsUsages[index]['cpu'][vm_i])
                return False

            if vmtemplate['net']<pop.vmsUsages[index]['net'][vm_i]:
#                print "NET usage constraint not satified for solution "+str(index)+ " and VM "+str(vm_i)
#                print "template value "+str(vmtemplate['net']) + " and usage value "+str(pop.vmsUsages[index]['net'][vm_i])
                return False
                return False

            if vmtemplate['io']<pop.vmsUsages[index]['io'][vm_i]:
#                print "IO usage constraint not satified for solution "+str(index)+ " and VM "+str(vm_i)
#                print "template value "+str(vmtemplate['io']) + " and usage value "+str(pop.vmsUsages[index]['io'][vm_i])
                return False

        return True

    def duplicatedReplicaInVM(self, blockChromosome,solnumber):
        """
        Checks the violation of the constraint related to place twice the same
        replica in the same DataNode/VM.
        Args:
            pop (populaiton instances): solution population
            index (int): index of the solution to check
        Return:
            True/False: if the constraint is violated (True) or not (False)
        """ 

        i=0
        limit = len(blockChromosome)
        while i < limit:
            

            if len(set(blockChromosome[i:i+self.system.replicationFactor]))<len(blockChromosome[i:i+self.system.replicationFactor]):

                print "Duplicated block in solution "+str(solnumber)+ " and piece "+str(i)
                return True
            i+=self.system.replicationFactor
        return False
        
        
    def checkConstraints(self,pop, index):
        """
        Checks the violation of the constraints of the model.
        Args:
            pop (populaiton instances): solution population
            index (int): index of the solution to check
        Return:
            True/False: if the any constraint is violated (False) or not (True)            
        """ 
             
        
        if self.duplicatedReplicaInVM(pop.population[index]['block'],index):
            return False
        
        if not self.resourceUsages(pop,index):
            return False
        return True
        

#******************************************************************************************
#   END Model constraints
#******************************************************************************************

#******************************************************************************************
#   Unavailability calculation
#******************************************************************************************
    def vmFailureCurve(self,minvalue,maxvalue,usage):
        """
        Calculates the VM failure probability for the given usage values.
        Args:
            minvalue (float): min failure value
            maxvalue (float): max failure value
            usagevalue (float): CPU usage value
        Return:
            The failure probability            
        """        
        
        return minvalue + usage * (maxvalue - minvalue)
    
    def pmFailureCurve(self,minvalue,maxvalue,usage):
        """
        Calculates the PM failure probability for the given usage values.
        Args:
            minvalue (float): min failure value
            maxvalue (float): max failure value
            usagevalue (float): CPU usage value
        Return:
            The failure probability            
        """         
        if usage > 0.3:
            return maxvalue - (usage/0.3) * (maxvalue-minvalue)
        else:
            return minvalue + (usage-0.3/0.7) * (maxvalue - minvalue) 

    def calculateUnavailability(self,chromosome,pmsusages,vmsusages):
        """
        Calculates the file unavailability for a solution.
        Args:
            chromosome (list of dictionaries): chromosomes of the solution
            pmsusages (list of dictionaries): PM usages for the current solution
            vmsusages (list of dictionaries): VM usages for the current solution
        Return:
            The file unavailability            
        """        

        
        blockChromosome = chromosome['block']
        
        failureTotal = 0.0
        
        
        listFailureVm = []
        for i,j in enumerate(chromosome['vm']):
            minfail = self.system.vmTemplate[chromosome['vmtype'][i]]['minfailrate']
            maxfail = self.system.vmTemplate[chromosome['vmtype'][i]]['maxfailrate']
            vmU = vmsusages['cpu'][i]
            listFailureVm.append(self.vmFailureCurve(minfail,maxfail,vmU))           

        listFailurePm = []
        for i in range(0,self.system.pmNumber):
            minfail = self.system.pmDefinition[i]['minfailrate']
            maxfail = self.system.pmDefinition[i]['maxfailrate']
            pmU = pmsusages['cpu'][i]
            
            listFailurePm.append(self.pmFailureCurve(minfail,maxfail,pmU))         


        i=0
        limit = len(blockChromosome)
        while i < limit:
            
            #calculation of the unavailability of each set of replicas of the same block
            
            blockVmReplicas = blockChromosome[i:i+self.system.replicationFactor]
            
            
            blockPmReplicas = []
            
            #two list, one for the vms where the replicas are stored 
            #and another one for the pms where the replicas are stored
            
            for k in range(0,len(blockVmReplicas)):
                blockPmReplicas.append(chromosome['vm'][blockVmReplicas[k]])
                
            setPmReplicas = set(blockPmReplicas)

            
            failureBlock = 1.0
            
            for pm_i in setPmReplicas:
                
                
                elements=[y for y,x in enumerate(blockPmReplicas) if x==pm_i]
                 
                # i need to calculate failure(pm)+ PRODCT [failure(vms)] for each
                #machiner where a block is stored. I calculate the set of vms in
                # the same pm.
                failurePm = listFailurePm[blockPmReplicas[elements[0]]]
                
                failureVm = 1.0
                
                for i_e,v_e in enumerate(elements):
                    failureVm *= listFailureVm[blockVmReplicas[v_e]]
                
                failureBlock *= (failurePm + failureVm)
                
            failureTotal += failureBlock
            i+=self.system.replicationFactor
         
        #To calculate the mean value
        failureTotal = failureTotal / (len(blockChromosome)/self.system.replicationFactor)

        return failureTotal





#******************************************************************************************
#   END Unavailability calculation
#******************************************************************************************


#******************************************************************************************
#   ResourceWaste calculation
#******************************************************************************************

    def calculateResourceWaste(self, solutionPmsUsages):
        """
        Calculates the resource waste for a solution.
        Args:
            solutionPmsUsages (list of dictionaries): PM usages for the current solution
        Return:
            The resource waste value           
        """
        resourceWaste = 0.0        
        for i in range(0,self.system.pmNumber):
            cpuUsage = solutionPmsUsages['cpu'][i] / self.system.pmDefinition[i]['cpu']
            netUsage = solutionPmsUsages['net'][i] / self.system.pmDefinition[i]['net']
            ioUsage = solutionPmsUsages['io'][i] / self.system.pmDefinition[i]['io']
            
            datos = [cpuUsage, netUsage, ioUsage]           
            sumUsage = np.sum(datos)
            stdUsage = np.std(datos)
            
            if sumUsage > 0.0:
                resourceWaste += (stdUsage + self.system.epsilomResourceWaste) / sumUsage
            
        return resourceWaste

#******************************************************************************************
#   END ResourceWaste calculation
#******************************************************************************************


#******************************************************************************************
#   Energy calculation
#******************************************************************************************

    def calculateEnergy(self, solutionPmsUsages):
        """
        Calculates the power consumption for a solution.
        Args:
            solutionPmsUsages (list of dictionaries): PM usages for the current solution
        Return:
            The power consumption value           
        """

        energyConsumption = 0.0        
        for i in range(0,self.system.pmNumber):
            
            Prh = self.system.pmDefinition[i]['energyMax'] - self.system.pmDefinition[i]['energyIdle']
            
            cpuUsage = solutionPmsUsages['cpu'][i] / self.system.pmDefinition[i]['cpu']
            netUsage = solutionPmsUsages['net'][i] / self.system.pmDefinition[i]['net']
            ioUsage = solutionPmsUsages['io'][i] / self.system.pmDefinition[i]['io']
            
            if cpuUsage <= self.system.pmDefinition[i]['energyLambda']:
                energyCPU = self.system.pmDefinition[i]['energyAlpha'] * Prh * cpuUsage
            else:
                energyCPU = self.system.pmDefinition[i]['energyBeta'] * Prh + (1 - self.system.pmDefinition[i]['energyBeta']) * Prh * cpuUsage

            energyNET = self.system.pmDefinition[i]['energyGamma'] * Prh * netUsage
            energyIO = self.system.pmDefinition[i]['energyDelta'] * Prh * ioUsage


            
            energyConsumption += energyCPU + energyNET + energyIO
            
        return energyConsumption

#******************************************************************************************
#   END Energy calculation
#******************************************************************************************






#******************************************************************************************
#   Objectives and fitness calculation
#******************************************************************************************


    def calculateFitnessObjectives(self, pop, index):
        """
        Calculates the three objectives values of a solution and checks if the 
        constraint are violated or not. If violated, the fitness values are set
        to infinite.
        Args:
            pop (populaiton instance): the set of solutions of the population
            index (int): the solution to be calculated and measured
        Return:
            The fitness / objective values           
        """

        chr_fitness = {}
        chr_fitness["index"] = index
        
        chromosome=pop.population[index]
        
        pmsUsages=pop.pmsUsages[index]
        vmsUsages=pop.vmsUsages[index]
        
        if self.checkConstraints(pop,index):
            
            chr_fitness["energy"] = self.calculateEnergy(pmsUsages)
            
            chr_fitness["unavailability"] = self.calculateUnavailability(chromosome,pmsUsages,vmsUsages)

            chr_fitness["resourcewaste"] = self.calculateResourceWaste(pmsUsages)
        
        else:
#            print ("not constraints")
            chr_fitness["energy"] = float('inf')
            chr_fitness["unavailability"] = float('inf')
            chr_fitness["resourcewaste"] = float('inf')
            
        return chr_fitness
        
    def calculatePopulationFitnessObjectives(self,pop):  
        """
        Calculates the fitness values for all the solutions in the population.
        Args:
            pop (populaiton instance): the set of solutions of the population
        """        
        pre = datetime.now()
        
        for index,citizen in enumerate(pop.population):
            cit_fitness = self.calculateFitnessObjectives(pop,index)
            pop.fitness[index] = cit_fitness
            
        if self.printTimes:
            print "Total fitness and constraints : "+ str(datetime.now() - pre)
        
         
    
#******************************************************************************************
#   END Objectives and fitness calculation
#******************************************************************************************


    def removeEmptyVms(self,chromosome):
        """
        Normalizes the VM in the vm-chromosome. From the execution of some crossover
        or mutation, some VM can not longer allocate a block in a given solution. In
        those cases, the VM is removed from the vm-chromosome. The identifications of
        all the VM are normalized to the values of 0 to Number of vms (after been removed).
        Args:
            pop (populaiton instance): the set of solutions of the population
        """        
        
        usedVms =  [ 0 for i in range(0,len(chromosome['vm']))]
        
        for i,v in enumerate(chromosome['block']):
            usedVms[v]=1
    
        
        vmShiftPosition = []
        shiftValue = 0
        quantityRemoved = 0
        for i,v in enumerate(usedVms):
            vmShiftPosition.append(shiftValue)
            if v==0:
                shiftValue += 1
                chromosome['vm'].pop(i-quantityRemoved)
                chromosome['vmtype'].pop(i-quantityRemoved)
                quantityRemoved +=1
        
        
        for i in range(0,len(chromosome['block'])):
            chromosome['block'][i] = chromosome['block'][i] - vmShiftPosition[chromosome['block'][i]]
            
        
        
        
            




#******************************************************************************************
#   NSGA-II Algorithm
#******************************************************************************************

            
    def dominates(self,a,b):
        """
        Checks if solution A dominates solution B.
        Args:
            a (list of dictionaries): the fitness/objective values of a solution
            b (list of dictionaries): the fitness/objective values of a solution
        Return
            True/False: if solution A dominates solution B
        """ 
        #checks if solution a dominates solution b, i.e. all the objectives are better in A than in B
        Adominates = True
        #### OJOOOOOO Hay un atributo en los dictionarios que no hay que tener en cuenta, el index!!!
        for key in a:
            if key!="index":  #por ese motivo está este if.
                if b[key]<=a[key]:
                    Adominates = False
                    break
        return Adominates        

        
    def crowdingDistancesAssigments(self,popT,front):
        """
        Calculates the crowding distances of the solutions in a front.
        Args:
            popT (population instance): the solutions in the population
            front (set): set of solutions in a front
        """         
        for i in front:
            popT.crowdingDistances[i] = float(0)
            
        frontFitness = [popT.fitness[i] for i in front]
        #OJOOOOOO hay un atributo en el listado que es index, que no se tiene que tener en cuenta.
        for key in popT.fitness[0]:
            if key!="index":   #por ese motivo está este if.
                orderedList = sorted(frontFitness, key=lambda k: k[key])
                
                popT.crowdingDistances[orderedList[0]["index"]] = float('inf')
                minObj = orderedList[0][key]
                popT.crowdingDistances[orderedList[len(orderedList)-1]["index"]] = float('inf')
                maxObj = orderedList[len(orderedList)-1][key]
                
                normalizedDenominator = float(maxObj-minObj)
                if normalizedDenominator==0.0:
                    normalizedDenominator = float('inf')
        
                for i in range(1, len(orderedList)-1):
                    popT.crowdingDistances[orderedList[i]["index"]] += (orderedList[i+1][key] - orderedList[i-1][key])/normalizedDenominator

    def calculateCrowdingDistances(self,popT):
        """
        Calculates the crowding distances for all the fronts and solutions.
        Args:
            popT (population instance): the solutions in the population
        """         
        
        i=0
        while len(popT.fronts[i])!=0:
            self.crowdingDistancesAssigments(popT,popT.fronts[i])
            i+=1


    def calculateDominants(self,popT):
        """
        Calculates, for each solution, the solutions that the given solution dominates to,
        and the solutions that the given solution is dominated by.
        Args:
            popT (population instance): the solutions in the population
        """         
        for i in range(len(popT.population)):
            popT.dominatedBy[i] = set()
            popT.dominatesTo[i] = set()
            popT.fronts[i] = set()

        for p in range(len(popT.population)):
            for q in range(p+1,len(popT.population)):
                if self.dominates(popT.fitness[p],popT.fitness[q]):
                    popT.dominatesTo[p].add(q)
                    popT.dominatedBy[q].add(p)
                if self.dominates(popT.fitness[q],popT.fitness[p]):
                    popT.dominatedBy[p].add(q)
                    popT.dominatesTo[q].add(p)        

    def calculateFronts(self,popT):
        """
        Calculates the sucessive front in the population.
        Args:
            popT (population instance): the solutions in the population
        """ 

        addedToFronts = set()
        
        i=0
        while len(addedToFronts)<len(popT.population):
            popT.fronts[i] = set([index for index,item in enumerate(popT.dominatedBy) if item==set()])
            addedToFronts = addedToFronts | popT.fronts[i]
            
            for index,item in enumerate(popT.dominatedBy):
                if index in popT.fronts[i]:
                    popT.dominatedBy[index].add(-1)
                else:
                    popT.dominatedBy[index] = popT.dominatedBy[index] - popT.fronts[i]
            i+=1        
            
    def fastNonDominatedSort(self,popT):
        """
        Calculates the fronts of a population.
        Args:
            popT (population instance): the solutions in the population
        """         
        self.calculateDominants(popT)
        self.calculateFronts(popT)
             
                
#******************************************************************************************
#   END NSGA-II Algorithm
#******************************************************************************************


#******************************************************************************************
#   Evolution based on NSGA-II 
#******************************************************************************************

    def generateRoundRobin1D(self, mylistsize, mylistrange):
        """
        Generates a chromosome with a round-robin distribution of its values.
        Args:
            mylistsize (int): the size of the list to create
            mylistrange (int): the values to include "round-robin"-ly in the list
        Return:
            The round-robin generated distribution
        """ 
        
        mylist = []
        rangelist = range(0,mylistrange)
        while len(mylist)<mylistsize:
            mylist += rangelist
        mylist=mylist[0:mylistsize]
        return mylist


    def generateRoundRobin2Dshuffle(self, mylistsize, piecesize, mylistrange):
        """
        Generates a block-chromosome with a round-robin distribution of its values
        but shuffling the values for all the replicas or a chunk.
        Args:
            mylistsize (int): the size of the list to create
            mylistrange (int): the values to include "round-robin"-ly in the list
            mylistrange (int): the subpart (replicas of a chunk) to be shuffle
        Return:
            A two dimension array with the round robin distribution generated and the shuffle of the chunk replicas
        """         
        mylist = self.generateRoundRobin1D(mylistsize,mylistrange)


        i=0
        mylist2=[]
        while i<len(mylist):
            tmppiece=mylist[i:i+piecesize]
            self.rndPOP.shuffle(tmppiece)
            mylist2.append(tmppiece)
            i+=piecesize
        self.rndPOP.shuffle(mylist2)
        return mylist2

    def serialize2D(self, mylist2):
        """
        Function used after generateRoundRobin2Dshuffle to transform the two dimension array
        generated into a list (or 1 dimesion array.
        Args:
            mylistsize (list of list): the two dimension array
        Return:
            The one dimension array
        """     
        
        finallist=[]
        for i in mylist2:
            for j in i:
                finallist.append(j)
        return finallist
    
    


    def generatePopulation(self,popT):
        """
        Generates the initial population for the execution of the GA.
        Args:
            popT (population instance): the solutions in the population (that is initially empty)
        """ 
        
        
        for individual in range(self.populationSize):
            chromosome = {}
        
        
            if self.experimentScenario=='BOTH': 
                vmNumber = max(self.rndPOP.randint(1,self.system.vmNumber),self.system.pmNumber)


            if self.experimentScenario=='VM':
                vmNumber = max(self.rndPOP.randint(1,self.system.vmNumber),self.system.pmNumber)


            #if the optimization is done only by managing the blocks, the number of vms
            #is equal to the number of pms and there is a 1:1 mapping between pms and vms

            if self.experimentScenario=='BLOCK':
                vmNumber = self.system.pmNumber

            block = []

            if self.experimentScenario=='VM':
                block = self.generateRoundRobin1D(self.system.replicaNumber,vmNumber)
            
            if self.experimentScenario=='BLOCK' or self.experimentScenario=='BOTH':   
                block = self.generateRoundRobin2Dshuffle(self.system.replicaNumber,self.system.replicationFactor,vmNumber)
                block = self.serialize2D(block)
            
            #Si en lugar de round robin queremos aleatorio, descomentar la siguiente linea
            #block = [random.randint(0,vmNumber-1) for i in range(0,self.system.replicaNumber) ]
            
            vm = []
            vm = self.generateRoundRobin1D(vmNumber,self.system.pmNumber)
            
            
            
            vmtype = []
            vmtype = self.generateRoundRobin1D(vmNumber,len(self.system.vmTemplate))


            if self.experimentScenario=='BOTH':
                self.rndPOP.shuffle(vm)
                self.rndPOP.shuffle(vmtype)
                
               
            if self.experimentScenario=='VM':
                self.rndPOP.shuffle(vmtype)            
                self.rndPOP.shuffle(vm)            
            
            chromosome['block']=block
            chromosome['vm']=vm
            chromosome['vmtype']=vmtype
            
            self.removeEmptyVms(chromosome)
            
            popT.population[individual]=chromosome
            popT.dominatedBy[individual]=set()
            popT.dominatesTo[individual]=set()
            popT.fronts[individual]=set()
            popT.crowdingDistances[individual]=float(0)
            
        self.calculateSolutionsWorkload(popT)
        self.calculatePopulationFitnessObjectives(popT)
#        self.fastNonDominatedSort(popT)
#        self.calculateCrowdingDistances(popT)

    def tournamentSelection(self,k,popSize):
        """
        Selects a father using the tournament selection operator
        Args:
            k (int): Number of rounds of the tournament selection operator
            popSize (int): population size
        Return:
            The selected father
        """ 

        selected = sys.maxint 
        for i in range(k):
            selected = min(selected,self.rndEVOL.randint(0,popSize-1))
        return selected
           
    def fatherSelection(self, orderedFathers):
        """
        Selects a father
        Args:
            orderedFatthers (list): the father ordered by the NSGA-2 conditions (fronts and crowding distance)
        Return:
            The selected father
        """         
        i = self.tournamentSelection(2,len(orderedFathers))
        return  orderedFathers[i]["index"]
        




    def evolveToOffspring(self):
        """
        Generates the offspring from the current population.
        Return:
            The population of the offspring
        """ 
        
        offspring = pop.POPULATION(self.populationSize)
        offspring.population = []

        orderedFathers = self.crowdedComparisonOrder(self.populationPt)
        

        #offspring generation

        while len(offspring.population)<(self.populationSize):
            father1 = self.fatherSelection(orderedFathers)
            father2 = father1
            while father1 == father2:
                father2 = self.fatherSelection(orderedFathers)
            #print "[Father selection]: Father1: %i **********************" % father1
            #print "[Father selection]: Father1: %i **********************" % father2
            
            self.crossover(self.populationPt.population[father1],self.populationPt.population[father2],offspring.population)
        
        #offspring mutation
        
        for index,children in enumerate(offspring.population):
            if self.rndEVOL.uniform(0,1) < self.mutationProbability:
                self.mutate(children)
                #print "[Offsrping generation]: Children %i MUTATED **********************" % index
            
        #print "[Offsrping generation]: Population GENERATED **********************"  
        
        return offspring

        
    def crowdedComparisonOrder(self,popT):
        """
        Creates a order list with the solutions considering, first the front, and secondly, the crowding disntace
        Args:
            popT (population instance): the population of the solutions
        Return:
            The ordered list

        """ 
        valuesToOrder=[]
        for i,v in enumerate(popT.crowdingDistances):
            citizen = {}
            citizen["index"] = i
            citizen["distance"] = v
            citizen["rank"] = 0
            valuesToOrder.append(citizen)
        
        f=0    
        while len(popT.fronts[f])!=0:
            for i,v in enumerate(popT.fronts[f]):
                valuesToOrder[v]["rank"]=f
            f+=1
             
        return sorted(valuesToOrder, key=lambda k: (k["rank"],-k["distance"]))



        
    def evolveAIA(self):
        """
        Generates the offspring from the current population for the AIA algorithm.
        Return:
            The population of the offspring
        """ 

        
        offspring = pop.POPULATION(self.populationSize)
        offspring.population = []

        orderedFathers = self.crowdedComparisonOrder(self.populationPt)
        

        #offspring generation

        while len(offspring.population)<self.populationSize:
            father1 = self.fatherSelection(orderedFathers)
            children = copy.deepcopy(self.populationPt.population[father1])
            if self.rndEVOL.uniform(0,1) < self.mutationProbability:
                self.mutate(children)
            offspring.population.append(children)
            
        self.populationPt = offspring
       
        self.calculateSolutionsWorkload(self.populationPt)
        self.calculatePopulationFitnessObjectives(self.populationPt)
        self.fastNonDominatedSort(self.populationPt)
        self.calculateCrowdingDistances(self.populationPt)        
                 
            
        
        return offspring


        
       
    def evolveNSGA2(self):
        """
        Main part of the NSGA-2 algorithm. It iterates the algorithm for one generation/iteration.
        """ 
        
        offspring = pop.POPULATION(self.populationSize)
        offspring.population = []

        pre=datetime.now()
        offspring = self.evolveToOffspring()
        if self.printTimes:
            print "Population evolution: "+ str(datetime.now() - pre)
        
        
        pre=datetime.now()
        self.calculateSolutionsWorkload(offspring)
        if self.printTimes:
            print "Workload calculation: "+ str(datetime.now() - pre)
        
        self.calculatePopulationFitnessObjectives(offspring)
        
       
        
        populationRt = offspring.populationUnion(self.populationPt,offspring)
        
        pre=datetime.now()
        self.fastNonDominatedSort(populationRt)
        self.calculateCrowdingDistances(populationRt)
        
        
        orderedElements = self.crowdedComparisonOrder(populationRt)
        if self.printTimes:
            print "NSGA-II: "+ str(datetime.now() - pre)
        
        
        
        finalPopulation = pop.POPULATION(self.populationSize)
        
        for i in range(self.populationSize):
            finalPopulation.population[i] = populationRt.population[orderedElements[i]["index"]]
            finalPopulation.fitness[i] = populationRt.fitness[orderedElements[i]["index"]]
            finalPopulation.vmsUsages[i] = populationRt.vmsUsages[orderedElements[i]["index"]]

        for i,v in enumerate(finalPopulation.fitness):
            finalPopulation.fitness[i]["index"]=i        
        
        self.populationPt = finalPopulation
        
        
        self.fastNonDominatedSort(self.populationPt)
        self.calculateCrowdingDistances(self.populationPt)
        


        
       
        

#******************************************************************************************
#  END Evolution based on NSGA-II 
#******************************************************************************************



