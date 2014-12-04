import re

def lp_solve():
    file = open("lp_solve.out", 'r')
    pattern = re.compile("[ ]+[0-9]+[.]{0,1}[0-9]*")
    VoOF = ""
    VotV = []
    
    for line in file:
        if(re.match("Value of objective function:", line)):
            VoOF = re.findall(pattern, line)[0]
        elif(re.match("x", line)):
            x = re.findall(pattern, line)[0]
            VotV.append(float(x))
    
    results = {'VoOF':0.0, 'VotV':[]}
    results['VoOF'] = float(VoOF)
    results['VotV'] = VotV
    
    return results

def glpk():
    file = open("glpk.out", 'r')
    pattern = re.compile("[ ]+[0-9]+[.]{0,1}[0-9]*")
    x_pattern = re.compile("\s+\d+\s+x")
    VoOF = ""
    VotV = []
    
    for line in file:
        if(re.match("Objective:", line)):
            VoOF = re.findall(pattern, line)[0]
        elif(x_pattern.search(line) != None):
            x = re.findall(pattern, line)[1]
            VotV.append(float(x))
    
    results = {'VoOF':0.0, 'VotV':[]}
    results['VoOF'] = float(VoOF)
    results['VotV'] = VotV
    
    return results

def cplex():
    file = open("cplex.sol", 'r')
    pattern = re.compile("[0-9]+[.]{0,1}[0-9]*")
    VoOF = ""
    VotV = []
    
    for line in file:
        if(re.search("objectiveValue=", line) != None):
            VoOF = re.findall(pattern, line)[0]
        elif(re.search("variable name=", line) != None):
            x = re.findall(pattern, line)[2]
            VotV.append(float(x))
    
    results = {'VoOF':0.0, 'VotV':[]}
    results['VoOF'] = float(VoOF)
    results['VotV'] = VotV
    
    return results

