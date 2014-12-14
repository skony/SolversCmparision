'''
Created on 11 gru 2014

@author: piotrek
'''
import glob
import itertools
import os
import re

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

def getTimeVariablesData(solvers, results_dir):
    rating = {"ids":[]}
    for s in solvers:
        rating[s["id"]] = []
        rating["ids"].append(s["id"])
    rating["x"] = []
    num = re.compile("\d+")
    dec = re.compile("\d+[.]\d+")
    str = re.compile("[a-z]+_?[a-z]*")
    os.chdir(results_dir)
    for file in glob.glob("*"):
        rfile = open(file, 'r')
        for line in rfile:
            if(re.search("Number of variables:", line) != None):
                x = re.findall(num, line)[0]
                rating["x"].append(float(x))
            elif(re.search("\d+ms", line) != None):
                x = re.findall(dec, line)[0]
                id = re.findall(str, line.rsplit("ms")[1])[0]
                rating[id].append(float(x))
                
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
    
def drawLineChart(solvers, results_dir, charts_dir):
    rating = getTimeVariablesData(solvers, results_dir)
    fig, ax = plt.subplots()
    marker = itertools.cycle((',', '+', '.', 'o', '*')) 
    
    for s in rating["ids"]:
        order = np.argsort(rating['x'])
        xs = np.array(rating['x'])[order]
        ys = np.array(rating[s])[order]
        plt.plot(xs, ys, label=s, marker=next(marker))
        
    plt.xlabel("Number of variables")
    plt.ylabel("Time in miliseconds")
    plt.legend(loc='upper left')
    plt.savefig(charts_dir + "time_from_variables.png") 