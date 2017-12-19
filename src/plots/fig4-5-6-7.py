#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Copyright 2017 Carlos Guerrero, Isaac Lera.

Created on Mon Nov 18 09:15:02 2017
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
import numpy as np


sns.set(style="white", palette="bright", color_codes=True)


executionId= '20171130150009'


file_path = "./"+executionId
file_pathResult = "./"+executionId+"plots"
calculateReliability = False
numberofGenerations=300

df = pd.read_csv(file_path+'/agregatedResultsUK.csv',sep=';')


cases =[]
cases.append(['pm',50])
cases.append(['pm',200])
cases.append(['filenumber',200])
cases.append(['filenumber',25])


for case in cases:
    
    outterElement = case[0]
    outterValue = case[1]
    
    df2 = df.loc[df[outterElement]== outterValue]
    
    
    for metric in ['energy','resource','unavalaibility']:
        
    
        if metric =='energy':
            myytitle = 'Power (Watts)'
            metrictitle = 'Power consumption'
        if metric =='resource':
            myytitle = 'Waste'
            metrictitle = 'Resource waste'
        if metric =='unavalaibility':
            myytitle = 'Unavalaibility (1/weeks)'
            metrictitle = 'File unavailability'       
        
        
        if outterElement == 'pm':      
            figtitleStr = metrictitle +" ("+str(outterValue) + " PMs)"
            innerElement = 'filenumber'
            myxtitle ='Number of files'
        if outterElement == 'filenumber':      
            figtitleStr = metrictitle +" ("+str(outterValue) + " files)"
            innerElement = 'pm'
            myxtitle ='Number of PMs'
            
    
    
    
    
            
    
        
        dfMetricBoth = df2.loc[df['scenario']== 'BOTH',[innerElement,metric]]
        dfMetricVm = df2.loc[df['scenario']== 'VM',[innerElement,metric]]
        dfMetricBlock = df2.loc[df['scenario']== 'BLOCK',[innerElement,metric]].loc[df['algorithm']=='NSGA2']
        dfMetricAIA = df2.loc[df['scenario']== 'BLOCK',[innerElement,metric]].loc[df['algorithm']=='AIA']
        
        dfMetricBoth=dfMetricBoth.replace([np.inf, -np.inf], 0)
        dfMetricVm=dfMetricVm.replace([np.inf, -np.inf], 0)
        dfMetricBlock=dfMetricBlock.replace([np.inf, -np.inf], 0)
        dfMetricAIA=dfMetricAIA.replace([np.inf, -np.inf], 0)
        
        minValue = min(dfMetricBoth[metric].min(),dfMetricVm[metric].min(),dfMetricBlock[metric].min(),dfMetricAIA[metric].min())
        maxValue = max(dfMetricBoth[metric].max(),dfMetricVm[metric].max(),dfMetricBlock[metric].max(),dfMetricAIA[metric].max())
        minLimit = minValue - 0.1*(maxValue-minValue)
        maxLimit = maxValue + 0.1*(maxValue-minValue)
        
        minLimit = max(0.0,minLimit)
        minLimit = 0.0
    
    
        fig, ax = plt.subplots(figsize=(8.0,4.0))
        index = np.arange(4)
        bar_width = 0.2
        opacity = 0.8
        
        fig.suptitle(figtitleStr, fontsize=18)
    
    
        rects1 = plt.bar(index, list(dfMetricBoth[metric]), bar_width,
                         alpha=opacity,
                         label='NSGA-both')   
        rects2 = plt.bar(index + bar_width, list(dfMetricVm[metric]), bar_width,
                         alpha=opacity,
                         label='NSGA-vm')  
        rects3 = plt.bar(index + 2*bar_width, list(dfMetricBlock[metric]), bar_width,
                         alpha=opacity,
                         label='NSGA-block')  
        rects4 = plt.bar(index + 3*bar_width, list(dfMetricAIA[metric]), bar_width,
                         alpha=opacity,
                         label='AIA-block')  
        
        plt.xticks(index + 3*bar_width / 2, list(dfMetricAIA[innerElement]))
    
    
        plt.ylim([minLimit,maxLimit])
        

        
        
        ax.set_xlabel(myxtitle, fontsize=18)
    
    
        ax.set_ylabel(myytitle, fontsize=18)
        #plt.ylim([0,2000])
        
        plt.legend(loc="upper center", ncol=4, fontsize=14, bbox_to_anchor=(0.45, 1.12))
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
    
    
        plt.grid()
        
        plt.show()
        
        fig.savefig(file_pathResult+'/fig-'+metric+str(outterValue)+outterElement+'.pdf',format='pdf')
    
        plt.close(fig)
    
        
    
        



     

    