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
from decimal import * 
from Main import problems_dir, results_dir
from numpy import arange,array,ones,linalg, append

def format_e(n):
    a = '%E' % n
    return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]

def getEquationSign(line):
    equation_pattern = re.compile("[=<>]+")
    return re.findall(equation_pattern, line)[0]

def getVars(line):
    var_pattern = re.compile("[a-zA-Z]+\w*")
    if ':' in line:
        return re.findall(var_pattern, line)[1:]
    else:
        return re.findall(var_pattern, line)

def getFactors(line):
    var_pattern = re.compile("[a-zA-Z]+\w*")
    factor_pattern = re.compile("[+ -]\d+[.]?\d*|[+-]")
    vars = re.findall(var_pattern, line)
    factors = re.findall(factor_pattern, line)
    factors2 = []
    if len(vars) == 1:  #line is bound not constraint
        factors2.append(1.0)
    for f in factors:
        if(f=='+'):
            factors2.append(1.0)
        elif(f=='-'):
            factors2.append(-1.0)
        else:
            factors2.append(float(f))
    return factors2

def checkIfCorrect(solvers, variables_dir, problems_dir, results_dir):
    solver_pattern = re.compile("\w+")
    var_pattern = re.compile("[a-zA-Z]+\w*")
    factor_pattern = re.compile("[\d+[.]\d+")
    e = Decimal("1e-12")
    os.chdir(problems_dir)
    for file in glob.glob("*"):
        solvers_correctness = {}
        curr_solver = ""
        solvers_vars = {}
        vfile = open(variables_dir + "/" + file + "VARIABLES", 'r')
        for line in vfile:
            if(line.startswith("***")):
                curr_solver = re.findall(solver_pattern, line.rsplit("VALUES", -1)[0].lower())[0]
                solvers_vars[curr_solver] = {}
                solvers_correctness[curr_solver] = Decimal(0.0)
            else:
                var = line.rsplit(" ", -1)[0]
                factor = float(line.rsplit(" ", -1)[1])
                solvers_vars[curr_solver][var] = factor
        solver_to_rm = []
        for s in solvers_vars.keys():
            if len(solvers_vars[s].keys()) == 0:
                solver_to_rm.append(s)
        for s in solver_to_rm:
            solvers_vars.pop(s)
            solvers_correctness.pop(s)
        vfile.close()
        if len(solvers_vars.keys()) == 0:
            continue
        with open(file) as pfile:
            next(pfile)
            for line in pfile:
                vars = getVars(line)
                factors = getFactors(line)
                equation = getEquationSign(line)
                for s in solvers_vars.keys():
                    rhs = Decimal(factors[-1])
                    ls = Decimal(0.0)
                    restart = False
                    for f, v in zip(factors, vars):
                        try:
                            vv = solvers_vars[s][v]
                        except KeyError:
                            #print( "solver " + s + " var " + v)
                            restart = True
                            break
                        ls += Decimal(f) * Decimal(vv)
                    if restart:
                        continue
                    if(equation == '=' and ls != rhs):
                        if solvers_correctness[s] < abs(ls - rhs):
                            diff = abs(ls - rhs)
                            solvers_correctness[s] = abs(ls - rhs)
                    elif((equation == '<' or equation == '<=') and ls > rhs):
                        if solvers_correctness[s] < abs(ls - rhs):
                            diff = abs(ls - rhs)
                            solvers_correctness[s] = abs(ls - rhs)
                    elif((equation == '>' or equation == '>=') and ls < rhs):
                        if solvers_correctness[s] < abs(rhs - ls):
                            diff = abs(rhs - ls)
                            solvers_correctness[s] = abs(rhs - ls)
        with open(results_dir + file + "RESULTS", 'a') as rfile:
            for s in solvers_correctness.keys():
                rfile.write(format_e(solvers_correctness[s]) + " biggest miscount [" + s + "]\n")

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
    exc_pattern = re.compile("([A-Z]+)_EXCEPTION")
    for s in solvers:
        rating[s["id"]] = {}
        rating[s["id"]]["timeout"] = 0
        rating[s["id"]]["any"] = 0
        if "exceptions" in s:
            for e in s["exceptions"].keys():
                 rating[s["id"]][e] = 0
    os.chdir(results_dir)
    for file in glob.glob("*"):
        problems_count += 1
        rfile = open(file, 'r')
        for line in rfile:   
            for solver in rating.keys():         
                if solver in line and "_EXCEPTION" in line:
                    exc = re.findall(exc_pattern, line)[0].rsplit("-", -1)[0]
                    rating[solver][exc.lower()] += 1
                    rating[solver]["any"] -= 1
                elif solver in line and " EXCEPTION" in line:
                    rating[solver]["any"] += 1              
        rfile.close()
    
    for solver in rating.keys():
        for e in rating[solver].keys():
            rating[solver][e] = int(rating[solver][e] / problems_count * 100)
    
    reversed_rating = {"timeout":[], "any":[], "ids":[]}
    for solver in rating.keys():
        reversed_rating["ids"].append(solver)
        for e in rating[solver].keys():
            if e not in reversed_rating.keys():
                reversed_rating[e] = []
    for s in reversed_rating["ids"]:
        for e in reversed_rating.keys():
            if e != "ids":
                if e in rating[s]:
                    reversed_rating[e].append(rating[s][e])
                else:
                    reversed_rating[e].append(0)
            
    return reversed_rating

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
    dec = re.compile("\d+[.]?\d*")
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
                    x = re.findall(dec, line)
                    if len(x) > 0:
                        rating["x"].append(float(x[0]))
                    else:
                        break
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
    color = itertools.cycle(('r', 'y', 'b', 'c', 'm', 'g', 'k', 'w'))
    bottom = [0]*len(rating["ids"])
    for r in rating.keys():
        if r != "ids":
            plt.bar(range(5), rating[r], color=next(color), label=r, bottom=bottom)
            bottom = [x + y for x, y in zip(bottom, rating[r])]

    ax.set_ylabel('Percentage')
    ax.set_title('Percentage of unresolved problems')
    ax.set_xticks([0,1,2,3,4])
    ax.set_xticklabels(tuple(rating["ids"]))
    plt.legend()
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
        A = array([xs, ones(len(xs))])
        w = linalg.lstsq(A.T, ys)[0]
        line = w[0] * xs + w[1]
        plt.plot(xs, line, label=s, marker=next(marker))
        #plt.plot(xs, ys, label=s, marker=next(marker))
    
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