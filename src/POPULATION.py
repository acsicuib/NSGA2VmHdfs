    #!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Copyright 2017 Carlos Guerrero, Isaac Lera.

Created on Wed Oct 16 08:10:55 2017
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

class POPULATION:
    """
    This class stores all the information related with a population. The population 
    is formed by "size" individuals, storing data related to the chromosome, fitness,
    fronts, dominators, dominated, crowding distances and resource usages for each solution.
    
    Attributes:
        population (list): List of "size" length with the dictionaris containing the chromosome of each individual.
            dictionary keys:
                'vm' (list): list with the genes for the vmallocation-chromosome
                'vmtype' (list): list with the genes for the vmtype-chromosome
                'block' (list): list with the genes for the block-chromosome
                
        vmsUsages (list): list of "size" length with the dictionaris cotaining the VM resource usages
            dictionary keys:
                'net' (list): list with the net bandwidth usage for each Vm in the solution
                'io' (list): list with the disk bandwidth usage for each Vm in the solution
                'cpu' (list): list with the cpu usage for each Vm in the solution
                
        pmsUsages (list): list of "size" length with the dictionaris cotaining the PM resource usages
            dictionary keys:
                'net' (list): list with the net bandwidth usage for each Pm in the solution
                'io' (list): list with the disk bandwidth usage for each Pm in the solution
                'cpu' (list): list with the cpu usage for each Pm in the solution
                
        fitness (list): list of "size" length with the dictionaris containing the objectives values
            dictionay keys:
                'energy' (float): power consumption for the solution
                'resourcewaste' (float): resource waste for the solution
                'unavailability' (float): file unavailability for the solution
                'index' (int): index for the solution position in the fitness list
                
        fitnessNormalized (list): list of "size" length with the dictionaris containing the normalized objectives values
            dictionay keys:
                'energy' (float): normalized power consumption for the solution
                'resourcewaste' (float): normalized resource waste for the solution
                'unavailability' (float): normalized file unavailability for the solution
                'fitness' (float): weigthed sum of the three previous objectives
                
        dominatesTo (list): list of "size" length with the set containing the solutions dominated by each solution
        
        dominatedBy (list): list of "size" length with the set containing the solutions that dominate each solution
        
        fronts (list): list of "size" length with the lists of set corresponding to each front for each solution
        
        crowdingDistnces (float): list of "size" length with the value for the Crowding Distance of each solution

    Args:
        size (int): population size

    """    
    def __init__(self,size):
        
        self.population = [{}]*size
        self.fitness = [{}]*size
        self.fitnessNormalized = [{}]*size
        self.dominatesTo = [set()]*size
        self.dominatedBy = [set()]*size
        self.fronts = [set()]*size
        self.crowdingDistances = [float(0)]*size
        self.vmsUsages = [list()]*size
        self.pmsUsages = [list()]*size
    
       
    
    def populationUnion(self,a,b):
        """
        Create a new population with the union of other 2 populations
        Args:
            a (POPULATION instance): first population
            b (POPULATION instance); second pupulation
        Returns:
            a new POPULATION instance with the union of two populations
        """       
        r=POPULATION(1)
        
        r.population = a.population + b.population
        r.vmsUsages = a.vmsUsages + b.vmsUsages
        r.pmsUsages = a.pmsUsages + b.pmsUsages
        r.fitness = a.fitness + b.fitness
        r.fitnessNormalized = a.fitnessNormalized + b.fitnessNormalized
        for i,v in enumerate(r.fitness):
            r.fitness[i]["index"]=i
        r.dominatesTo = a.dominatesTo + b.dominatesTo
        r.dominatedBy = a.dominatedBy + b.dominatedBy
        r.fronts = a.fronts + b.fronts
        r.crowdingDistances = a.crowdingDistances + b.crowdingDistances
        
        return r
        

        
    



