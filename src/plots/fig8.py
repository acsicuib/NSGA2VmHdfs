#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Copyright 2017 Carlos Guerrero, Isaac Lera.

Created on Mon Nov 22 14:23:58 2017
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
    
    figtitleStr = metrictitle
    myxtitle ='Experiment sizes'
        




        

    
    dfMetricBoth = df.loc[df['scenario']== 'BOTH',['pm','filenumber',metric]]
    dfMetricVm = df.loc[df['scenario']== 'VM',['pm','filenumber',metric]]
    
    dfMetricBoth=dfMetricBoth.replace([np.inf, -np.inf], 0)
    dfMetricVm=dfMetricVm.replace([np.inf, -np.inf], 0)

    
    minValue = min(dfMetricBoth[metric].min(),dfMetricVm[metric].min())
    maxValue = max(dfMetricBoth[metric].max(),dfMetricVm[metric].max())
    minLimit = minValue - 0.1*(maxValue-minValue)
    maxLimit = maxValue + 0.1*(maxValue-minValue)
    
    minLimit = max(0.0,minLimit)


    fig, ax = plt.subplots(figsize=(13,3))
    index = np.arange(16)
    bar_width = 0.2
    opacity = 0.8
    
    fig.suptitle(figtitleStr,fontsize=16)


    rects1 = plt.bar(index, list(dfMetricBoth[metric]), bar_width,
                     alpha=opacity,
                     label='NSGA-both')   
    rects2 = plt.bar(index + bar_width, list(dfMetricVm[metric]), bar_width,
                     alpha=opacity,
                     label='NSGA-vm')  

    
    itemtitles = list()
    
    for row in dfMetricBoth.iterrows():
        itemtitles.append(str(int(row[1]['pm']))+'p-'+str(int(row[1]['filenumber']))+'f')

    dfMetricBoth.reset_index(inplace=True)
    dfMetricVm.reset_index(inplace=True)
    
    speedup = dfMetricVm[metric].divide(dfMetricBoth[metric])
    speedup = speedup * 100
    speedup = speedup - 100
    
    height = pd.DataFrame([dfMetricBoth[metric],dfMetricVm[metric]]).max(axis=0)
    
    


    plt.xticks(index - bar_width, itemtitles, fontsize=12)
    plt.yticks(fontsize=12)
    plt.xticks(rotation=30)
    
    plt.ylim([minLimit,maxLimit])

    ax.set_ylabel(myytitle, fontsize=16)
    
    
# =============================================================================
#     #LINEA DE SEPARACION
# =============================================================================
#    xposition = [4, 8, 12]
#    for xc in xposition:
#        plt.axvline(x=xc-(2*bar_width), color='black', linestyle='-',linewidth=1.2)
#
#
    xcolor = ["orange","red","pink","gold"]
# =============================================================================
#     #BACKGROUND COLORS
# =============================================================================
    xposition = [0,4, 8, 12,16]
    for i,v in enumerate(xcolor):
        plt.axvspan(xposition[i]- (2*bar_width), xposition[i+1]-(2*bar_width), facecolor=v, alpha=0.1)
        
  
    
# =============================================================================
#     #TERCERA ESCALA
#     ## Aceleración actual
# =============================================================================
    ax2 = ax.twinx()
    plt.gca().set_color_cycle(xcolor)
    for i in [0,4,8,12]:
        imp = ax2.plot([i+0+bar_width/2,i+1+bar_width/2,i+2+bar_width/2,i+3+bar_width/2], [speedup[i+0],speedup[i+1],speedup[i+2],speedup[i+3]],marker="o",color='red',linewidth=1.0)
    ax2.set_ylabel('Improvement (%)', color='black', fontsize=16)
    for label in ax2.yaxis.get_majorticklabels():
        label.set_fontsize(12)


    bbox_props = dict(boxstyle="square,pad=0.0", fc="white", ec="white", lw=0,alpha=0.7)
    maxValue = max(speedup)
    for i, v in enumerate(speedup):
        alt = speedup[i]+maxValue*0.05
        if alt>maxValue:
            alt = speedup[i]-maxValue*0.1
        ax2.text(index[i] - 1.5*bar_width, alt, "%0.2f"%v+"%", color='black',backgroundcolor='white',bbox=bbox_props)
      
        
    scatter1_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", c='red', marker = 'o',markeredgecolor='red',markeredgewidth=1.0)
       

    ax.legend([scatter1_proxy,rects1,rects2], ['Improvement','NSGA-both','NSGA-vm'], loc="upper center", ncol=4, fontsize=12, bbox_to_anchor=(0.79, 1.18),handletextpad=0.1)


#    ax2.legend(loc="upper left", ncol=1, fontsize=12)
    
# =============================================================================
#     #TERCERA ESCALA
#     ## Aceleración ponderada por cada grupo de experimento
# =============================================================================
#    ax2 = ax.twinx()
#    aset = 0    
#    spR = []
#    for i,rs in enumerate(speedup):
#        if i%4==0:
#            aset = (speedup[i]+speedup[i+1]+speedup[i+2]+speedup[i+3])
#        spR.append(float(rs/aset))
#
#
#    plt.gca().set_color_cycle( ["orange","red","pink","blue"])
#    for i in [0,4,8,12]:
#        ax2.plot([i+0,i+1,i+2,i+3], [spR[i+0],spR[i+1],spR[i+2],spR[i+3]])
#    ax2.set_ylabel('Speedup', color='black')
#    
    
    

    plt.grid()
    plt.legend()
    
    plt.gcf().subplots_adjust(bottom=0.195)
    plt.gcf().subplots_adjust(left=0.06)
    plt.gcf().subplots_adjust(right=0.93)

    
    plt.show()
    
    fig.savefig(file_pathResult+'/fig-'+metric+'bothVSvm.pdf',format='pdf')

    plt.close(fig)
    
        
    
        




     

    