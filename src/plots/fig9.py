#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Copyright 2017 Carlos Guerrero, Isaac Lera.

Created on Mon Nov 19 18:02:15 2017
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
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt3d
import pandas as pd
import random as rand
import seaborn as sns
import pickle as pickle
import POPULATION as pop


sns.set(style="white", palette="muted", color_codes=True)


executionId= '20171130150009'


file_path = "./"+executionId
file_pathResult = "./"+executionId+"plots"

cases =[]


cases.append(['2p0','50','25'])
cases.append(['2p0','50','200'])
cases.append(['2p0','100','200'])
cases.append(['2p0','150','50'])
cases.append(['2p0','150','200'])
cases.append(['2p0','200','200'])



for case in cases:

    vm = case[0]
    pm = case[1]
    fs = case[2]
    
    
    BothfileName = '0-BOTH-NSGA2-TPDSmodel-vm'+vm+'-pm'+pm+'-fs'+fs+'-lastGeneration.pkl'
    VmfileName = '1-VM-NSGA2-TPDSmodel-vm'+vm+'-pm'+pm+'-fs'+fs+'-lastGeneration.pkl'
    BlockfileName = '2-BLOCK-NSGA2-TPDSmodel-vm'+vm+'-pm'+pm+'-fs'+fs+'-lastGeneration.pkl'
    AiafileName = '3-BLOCK-AIA-TPDSmodel-vm'+vm+'-pm'+pm+'-fs'+fs+'-lastGeneration.pkl'
    
    pkl_file = open(file_path+'/'+BothfileName, 'rb')
    BothLastGeneration = pickle.load(pkl_file)
    pkl_file.close()
    
    pkl_file = open(file_path+'/'+VmfileName, 'rb')
    VmLastGeneration = pickle.load(pkl_file)
    pkl_file.close()
    
    pkl_file = open(file_path+'/'+BlockfileName, 'rb')
    BlockLastGeneration = pickle.load(pkl_file)
    pkl_file.close()
    
    pkl_file = open(file_path+'/'+AiafileName, 'rb')
    AiaLastGeneration = pickle.load(pkl_file)
    pkl_file.close()
    
    
    titlecase = str(pm)+" PMs "+str(fs)+" files"
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    plt.gcf().subplots_adjust(left=0.00)

    a = [VmLastGeneration.fitness[v]["energy"] for i,v in enumerate(VmLastGeneration.fronts[0])]
    b = [VmLastGeneration.fitness[v]["resourcewaste"] for i,v in enumerate(VmLastGeneration.fronts[0])]
    c = [VmLastGeneration.fitness[v]["unavailability"] for i,v in enumerate(VmLastGeneration.fronts[0])]


    ax.scatter(a, b, c, color='green', marker="o")


    d = [BothLastGeneration.fitness[v]["energy"] for i,v in enumerate(BothLastGeneration.fronts[0])]
    e = [BothLastGeneration.fitness[v]["resourcewaste"] for i,v in enumerate(BothLastGeneration.fronts[0])]
    f = [BothLastGeneration.fitness[v]["unavailability"] for i,v in enumerate(BothLastGeneration.fronts[0])]


    ax.scatter(d, e, f, color='blue', marker="o", facecolors='none',linewidth='1')

    g = [BlockLastGeneration.fitness[v]["energy"] for i,v in enumerate(BlockLastGeneration.fronts[0])]
    h = [BlockLastGeneration.fitness[v]["resourcewaste"] for i,v in enumerate(BlockLastGeneration.fronts[0])]
    i = [BlockLastGeneration.fitness[v]["unavailability"] for i,v in enumerate(BlockLastGeneration.fronts[0])]


    ax.scatter(g, h, i, color='red', marker="o")
    
    
    j = [AiaLastGeneration.fitness[v]["energy"] for i,v in enumerate(AiaLastGeneration.fronts[0])]
    k = [AiaLastGeneration.fitness[v]["resourcewaste"] for i,v in enumerate(AiaLastGeneration.fronts[0])]
    l = [AiaLastGeneration.fitness[v]["unavailability"] for i,v in enumerate(AiaLastGeneration.fronts[0])]


    ax.scatter(j, k, l, color='purple', marker="o")
    


    scatter1_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", c='green', marker = 'o',markeredgecolor='green',markeredgewidth=1.0)
    scatter2_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", c='blue', marker = 'o',markerfacecolor='none',markeredgecolor='blue',markeredgewidth=1.0)
    scatter3_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", c='red', marker = 'o',markeredgecolor='red',markeredgewidth=1.0)
    scatter4_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", c='purple', marker = 'o',markeredgecolor='purple',markeredgewidth=1.0)
    ax.legend([scatter2_proxy, scatter1_proxy,scatter4_proxy, scatter3_proxy], ['NSGA-both','NSGA-vm', 'AIA-block', 'NSGA-block'], numpoints = 1, fontsize=12,ncol=2,handletextpad=0.1)



    ax.set_xlabel('Power consumption', fontsize=18)
    ax.set_ylabel('Resource waste', fontsize=18)
    ax.set_zlabel('File unavailability', fontsize=18)
    
    ax.tick_params(axis='x', which='major', pad=0)
    ax.tick_params(axis='y', which='major', pad=0)
    ax.tick_params(axis='z', which='major', pad=0)
    
    
    fig.savefig(file_pathResult+'/fig-pareto-vm'+vm+'-pm'+pm+'-fs'+fs+'.pdf')
    plt.close(fig)




     

    