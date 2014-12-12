'''
Created on 11 gru 2014

@author: piotrek
'''
import glob
import os

import matplotlib.pyplot as plt
import numpy as np


def getUnresolvedData(solvers, results_dir):
    rating = {}
    problems_count = 0
    for s in solvers:
        rating[s["id"]] = 0
    os.chdir(results_dir)
    for file in glob.glob("*"):
        rfile = open(file, 'r')
        problems_count += 1
        for line in rfile:
            for solver in rating.keys():
                if solver in line and " EXCEPTION" in line:
                    rating[solver] = rating[solver] + 1 
        rfile.close()
    
    for solver in rating.keys():
        rating[solver] = int(rating[solver] / problems_count * 100)
    
    return rating

def drawBarChart(solvers, results_dir, charts_dir):
    rating = getUnresolvedData(solvers, results_dir)
    fig, ax = plt.subplots()
    plt.bar(range(4), rating.values())

    ax.set_ylabel('Percentage')
    ax.set_title('Percentage of unresolved problems')
    ax.set_xticks([0,1,2,3])
    ax.set_xticklabels(tuple(rating.keys()))
    #plt.show()
    plt.savefig(charts_dir + "unresolved_problems.png")
    
        