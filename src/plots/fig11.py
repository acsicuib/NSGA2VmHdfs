#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Copyright 2017 Carlos Guerrero, Isaac Lera.

Created on Mon Nov 30 10:20:43 2017
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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import pandas as pd
import random as rand
import seaborn as sns
import pickle as pickle


sns.set(style="white", palette="muted", color_codes=True)


executionId= '20171130150009'


file_path = "./"+executionId
file_pathResult = "./"+executionId+"plots"

cases =[]
cases.append(['2p0','50','25'])
cases.append(['2p0','200','200'])


for case in cases:

    vm = case[0]
    pm = case[1]
    fs = case[2]
    
    
    BothfileName = '0-BOTH-NSGA2-TPDSmodel-vm'+vm+'-pm'+pm+'-fs'+fs+'-selectedSolution.pkl'
    VmfileName = '1-VM-NSGA2-TPDSmodel-vm'+vm+'-pm'+pm+'-fs'+fs+'-selectedSolution.pkl'
    
    pkl_file = open(file_path+'/'+BothfileName, 'rb')
    BothparetoResults = pickle.load(pkl_file)
    pkl_file.close()
    
    pkl_file = open(file_path+'/'+VmfileName, 'rb')
    VmparetoResults = pickle.load(pkl_file)
    pkl_file.close()
    
    
    
    for objective in ['energy','resourcewaste','unavailability']:
    
    
        if objective =='energy':
            myytitle = 'Power (Watts)'
            metrictitle = 'Power consumption'
        if objective =='resourcewaste':
            myytitle = 'Waste'
            metrictitle = 'Resource waste'
        if objective =='unavailability':
            myytitle = 'Unavalaibility (1/weeks)'
            metrictitle = 'File unavailability'       
        
        titlecase = str(pm)+" PMs "+str(fs)+" files"
        
        bothobjective = list()
        vmobjective = list()
        
        for i in range(0,len(BothparetoResults)):
            bothobjective.append(BothparetoResults[i]['fitness'][objective])
            vmobjective.append(VmparetoResults[i]['fitness'][objective])



        
    
        fig = plt.figure()

        fig.suptitle(metrictitle+" ("+titlecase+")", fontsize=18)
        ax = fig.add_subplot(111)

        ax.set_xlabel('Generations', fontsize=18)
        ax.set_ylabel(myytitle, fontsize=18)
        plt.gcf().subplots_adjust(left=0.15)
        ax.plot(bothobjective, label='NSGA-both', linewidth=2.0)
        ax.plot(vmobjective, label='NSGA-vm', linewidth=2.0, linestyle="-.")

        plt.legend(fontsize=14)
        plt.yticks(fontsize=14)
        plt.xticks(fontsize=14)

        plt.grid()
        fig.savefig(file_pathResult+'/fig-evol-'+objective+'-vm'+vm+'-pm'+pm+'-fs'+fs+'.pdf')
        plt.close(fig)   
    
    
    
        

    
    
    

    

  



     

    