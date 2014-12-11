'''
Created on 11 gru 2014

@author: piotrek
'''
import glob
import os
import matplotlib.pyplot as plt
import numpy as np

from Main import results_dir


def getUnresolvedData(solvers):
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
                    rating["solver"] = rating["solver"] + 1 
        rfile.close()
    
    for solver in rating.keys():
        rating["solver"] = rating["solver"] / problems_count
    
    return rating

def drawBarChart(solvers):
    rating = getUnresolvedData(solvers)
    
        