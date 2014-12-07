import re
import os
from warnings import catch_warnings

def lp_solve(output):
    VoOF = 0.0
    VotV = []
    results = {'VoOF':-0.0, 'VotV':[]}
    
    if(os.path.isfile(output + "lp_solve.out")):
        file = open(output + "lp_solve.out", 'r')
    else:
        return results
    
    file = open(output + "lp_solve.out", 'r')
    pattern = re.compile("[-+ ][0-9]+[.]{0,1}[0-9]*")
    VoOF = ""
    VotV = []
    
    for line in file:
        if(re.match("Value of objective function:", line)):
            VoOF = re.findall(pattern, line)[0]
#         elif(re.match("x", line)):
#             x = re.findall(pattern, line)[0]
#             VotV.append(float(x))
    
    try:
        results['VoOF'] = float(VoOF)
    except ValueError:
        results['VoOF'] = 0.0    
    results['VotV'] = VotV
    
    return results

def clp(output):
    VoOF = 0.0
    VotV = []
    results = {'VoOF':-0.0, 'VotV':[]}
    
    if(os.path.isfile(output + "clp.out")):
        file = open(output + "clp.out", 'r')
    else:
        return results
    
    file = open(output + "clp.out", 'r')
    pattern = re.compile("[-+ ][0-9]+[.]{0,1}[0-9]*")
    
    for line in file:
        if(re.match("Optimal - objective value", line)):
            VoOF = re.findall(pattern, line)[0]
#         elif(re.match("x", line)):
#             x = re.findall(pattern, line)[0]
#             VotV.append(float(x))
    
    try:
        results['VoOF'] = float(VoOF)
    except ValueError:
        results['VoOF'] = 0.0    
    results['VotV'] = VotV
    
    return results

def glpk(output):
    VoOF = 0.0
    VotV = []
    results = {'VoOF':-0.0, 'VotV':[]}
    
    if(os.path.isfile(output + "glpk.out")):
        file = open(output + "glpk.out", 'r')
    else:
        return results
    
    file = open(output + "glpk.out", 'r')
    pattern = re.compile("[-+ ][0-9]+[.]{0,1}[0-9]*")
    x_pattern = re.compile("\s+\d+\s+x")
    
    for line in file:
        if(re.match("Objective:", line)):
            VoOF = re.findall(pattern, line)[0]
#         elif(x_pattern.search(line) != None):
#             x = re.findall(pattern, line)[1]
#             VotV.append(float(x))
    
    try:
        results['VoOF'] = float(VoOF)
    except ValueError:
        results['VoOF'] = 0.0    
    results['VotV'] = VotV
    
    return results

def cplex(output):
    VoOF = 0.0
    VotV = []
    results = {'VoOF':-0.0, 'VotV':[]}
    
    if(os.path.isfile(output + "cplex.sol")):
        file = open(output + "cplex.sol", 'r')
    else:
        return results
    pattern = re.compile("[+-][0-9]+[.]{0,1}[0-9]*")
    
    for line in file:
        if(re.search("objectiveValue=", line) != None):
            VoOF = re.findall(pattern, line)[0]
#         elif(re.search("variable name=", line) != None):
#             x = re.findall(pattern, line)[2]
#             VotV.append(float(x))
    try:
        results['VoOF'] = float(VoOF)
    except ValueError:
        results['VoOF'] = 0.0      
    results['VotV'] = VotV
    
    return results

