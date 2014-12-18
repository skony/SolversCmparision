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

def getFactorMagnitude(f):
    f = abs(float(f))
    magnitude = 0
    while(f>=10.0 or f<1.0):
        if(f>=10.0):
            f /= 10
            magnitude += 1
        elif(f<1.0):
            f *= 10
            magnitude -= 1
     
    return magnitude   
    
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

#category
#-variables
#-constraits
#-matrix density(density)
#-factors diff(factors)
#-variables * constraints(multiplication)
def getTimeVariablesData(solvers, results_dir, category):
    rating = {"ids":[]}
    for s in solvers:
        rating[s["id"]] = []
        rating["ids"].append(s["id"])
    rating["x"] = []
    num = re.compile("\d+")
    dec = re.compile("\d+[.]\d+")
    str = re.compile("[a-z]+_?[a-z]*")
    os.chdir(results_dir)
    
    if(category == "variables"):
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
    elif(category == "constraints"):
        for file in glob.glob("*"):
            rfile = open(file, 'r')
            for line in rfile:
                if(re.search("Number of constraints:", line) != None):
                    x = re.findall(num, line)[0]
                    rating["x"].append(float(x))
                elif(re.search("\d+ms", line) != None):
                    x = re.findall(dec, line)[0]
                    id = re.findall(str, line.rsplit("ms")[1])[0]
                    rating[id].append(float(x))
    elif(category == "density"):
        for file in glob.glob("*"):
            rfile = open(file, 'r')
            for line in rfile:
                if(re.search("Constraints density:", line) != None):
                    x = re.findall(dec, line)[0]
                    rating["x"].append(float(x))
                elif(re.search("\d+ms", line) != None):
                    x = re.findall(dec, line)[0]
                    id = re.findall(str, line.rsplit("ms")[1])[0]
                    rating[id].append(float(x))
    elif(category == "factors"):
        for file in glob.glob("*"):
            rfile = open(file, 'r')
            max_factor = 0.0
            min_factor = 0.0
            for line in rfile:
                if(re.search("Maximum factor:", line) != None):
                    max_factor = re.findall(dec, line)[0]
                elif(re.search("Minimum factor:", line) != None):
                    min_factor = re.findall(dec, line)[0]
                elif(re.search("\d+ms", line) != None):
                    x = re.findall(dec, line)[0]
                    id = re.findall(str, line.rsplit("ms")[1])[0]
                    rating[id].append(float(x))
            diff = getFactorMagnitude(max_factor) - getFactorMagnitude(min_factor)
            rating["x"].append(float(diff))
    elif(category == "multiplication"):
        for file in glob.glob("*"):
            rfile = open(file, 'r')
            vars = 0.0
            cons = 0.0
            for line in rfile:
                if(re.search("Number of variables:", line) != None):
                    vars = re.findall(num, line)[0]
                elif(re.search("Number of constraints:", line) != None):
                    cons = re.findall(num, line)[0]
                    rating["x"].append(float(cons) * float(vars))
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

#category
#-variables
#-constraits
#-matrix density(density)
#-factors diff(factors)
#-variables * constraints(multiplication)
def drawLineChart(solvers, results_dir, charts_dir, category):
    rating = getTimeVariablesData(solvers, results_dir, category)
    fig, ax = plt.subplots()
    marker = itertools.cycle(('v', '+', 'D', 'o', '*')) 
    
    for s in rating["ids"]:
        order = np.argsort(rating['x'])
        xs = np.array(rating['x'])[order]
        ys = np.array(rating[s])[order]
        plt.plot(xs, ys, label=s, marker=next(marker))
    
    if(category == "variables"):
        plt.xlabel("Number of variables")
    elif(category == "constraints"):
        plt.xlabel("Number of constraints")
    elif(category == "density"):
        plt.xlabel("Constraints density")
    elif(category == "factors"):
        plt.xlabel("Diffrent between max and min factor")
    elif(category == "multiplication"):
        plt.xlabel("Multiplication of number of variables and number of constraints")
        
    plt.ylabel("Time in miliseconds")
    plt.legend(loc='upper left')
    plt.savefig(charts_dir + "time_from_" + category + ".png") 