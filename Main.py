#!/usr/bin/python
import sys
import glob
import os
import json
import time
import re
import subprocess
import input_translator
from signal import SIGTERM
import shlex

source = ""
script_dir = ""
outputs_dir = ""
problems_dir = ""
results_dir = ""
charts_dir = ""

def getConfiguredSolvers():
    global script_dir
    solvers = []
    script_dir = os.path.dirname(__file__)
    os.chdir("solvers")
    
    for file in glob.glob("*.json"):
        abs_path = script_dir + "/solvers/" + file
        json_file = open(abs_path)
        data = json.load(json_file)
        solvers.append(data)
        json_file.close()
    
    os.chdir("../")
    return solvers
    
def runSolver(solver, file_name):
    results = open(script_dir + "/results/" + file_name + "RESULTS", 'a')
    if(solver["input"] != "lp_solve"):
        trans_cmd = "input_translator." + solver["input"] + "(\"" + script_dir + "/problems/" + file_name + "\")"
        problem_file = eval(trans_cmd)
    else:
        problem_file = script_dir + "/problems/" + file_name
        
    file_out_path = script_dir + "/outputs/" + file_name + solver["id"] + "." + solver["out"]
    file_out = open(file_out_path, 'w')
    stdout = None
    
    command = ""
    for x in solver["run"]:
        if(x == "file_name"):
            x = problem_file
        elif(x == ">"):
            stdout = file_out
            break
        elif(x == "<"):
            stdout = file_out
            continue
        elif(x == "file_out"):
            x = file_out_path
        command += x + " "
    t1 = time.time()
    try:
        #p = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
        p = subprocess.Popen(shlex.split(command), stdout=stdout)          
        p.wait(timeout = 10)
        t2 = time.time()
        ts = ((t2-t1)*1000).__str__()
        results.write(ts + "ms " + solver["id"] + "\n")
    except:
        os.kill(p.pid, SIGTERM)
        t2 = time.time()
        ts = ((t2-t1)*1000).__str__()
        results.write(ts + "ms TIMEOUT_EXCEPTION " + solver["id"] + "\n")
        
def getProblemParams(file_path):
    problem = open(file_path, 'r')
    os.chdir("../")
    os.chdir("results")
    results = open(file_path + "RESULTS", 'a')
    os.chdir("../")
    os.chdir("problems")
    pattern = re.compile("\w+:")
    NoV = 0
    NoC = 0
    NoViC = 0
    cons = False
    max = 1
    min = 1
    factor = re.compile("[\+\-\s][0-9]+[.]{0,1}[0-9]*")
     
    for line in problem:
        if(re.match("min:", line) and cons==False):
            NoV += line.count('+')
            NoV += line.count('-')
            cons = True
            factors = re.findall(factor, line)
            for f in factors:
                ff = float(f)
                if(ff > max):
                    max = ff
                if(abs(ff) < abs(min) and abs(ff) != 0):
                    min = ff
        elif(re.match(pattern, line)):
            NoC += 1
            if(line.count('<') == 1):
                ls = line.rsplit('<', -1)[0]    #ls = left side
                NoViC += ls.count('+')
                NoViC += ls.count('-')
            elif(line.count('>') == 1):
                ls = line.rsplit('>', -1)[0]    #ls = left side
                NoViC += ls.count('+')
                NoViC += ls.count('-')
            elif(line.count('=') == 1):
                ls = line.rsplit('>', -1)[0]    #ls = left side
                NoViC += ls.count('+')
                NoViC += ls.count('-')            
            factors = re.findall(factor, line)
            for f in factors:
                ff = float(f)
                if(ff > max):
                    max = ff
                if(abs(ff) < abs(min) and abs(ff) != 0):
                    min = ff
     
    results.write("Number of variables: " + NoV.__str__() + "\n")
    results.write("Number of constraints: " + NoC.__str__() + "\n")
    if(NoV * NoC != 0):
        CD = (NoViC.__float__() / (NoV * NoC)).__str__()
    else:
        CD = "err"
    results.write("Constraints density: " + CD + "\n")
    results.write("Maximum factor: " + max.__str__() + "\n")
    results.write("Minimum factor: " + min.__str__() + "\n")
    
    problem.close()
    results.close()
    
def scanOutput(solver, problem):
    full_path = outputs_dir + problem + solver["id"] + "." + solver["out"]
    if(os.path.isfile(full_path)):
        file = open(full_path, 'r')
    else:
        return
    
    VoOF = -0.0
    pattern = re.compile("[-+ ]?[0-9]+[.]?[0-9]*e?[+-]?[0-9]*")
    for line in file:
        if(re.search(solver["VoOF"], line) != None):
            list = re.findall(pattern, line)
            if(len(list) > 0):
                try:
                    VoOF = float(list[0])
                except ValueError:
                    VoOF = -0.0 

    file2 = open(results_dir + problem + "RESULTS", 'a')
    if(VoOF != -0.0):
        file2.write(VoOF.__str__() + " Value of objective function [" + solver["id"] + "]" + "\n")
    else:
        file2.write(VoOF.__str__() + " Value of objective function EXCEPTION [" + solver["id"] + "]" + "\n")
#         i = 1
#         for x in d["VotV"]:
#             file.write(x.__str__() + " x" + i.__str__() + " [" + solver["id"] + "]\n")
#             i += 1
    file.close()
    file2.close()
            
def cleanBefore(solvers):
    os.chdir(results_dir)
    for file in glob.glob("*"):
        os.unlink(file)
        
    os.chdir(outputs_dir)
    for file in glob.glob("*"):
        os.unlink(file)
    
    os.chdir(problems_dir)
    for file in glob.glob("*"):
        for solver in solvers:
            if solver["input"] in file:
                os.unlink(file)
                break
    
    os.chdir("../")
    
def cleanAfter(solvers):
    os.chdir(problems_dir)
    for file in glob.glob("*"):
        for solver in solvers:
            if solver["input"] in file:
                os.unlink(file)
                break
    os.chdir("../")
           
def main(argv):
    global script_dir
    global outputs_dir
    global problems_dir
    global results_dir
    script_dir = os.path.dirname(__file__)
    outputs_dir = script_dir + "/outputs/"
    problems_dir = script_dir + "/problems/"
    results_dir = script_dir + "/results/"
    
    solvers = getConfiguredSolvers()
    cleanBefore(solvers)
    global source
    
    if(argv[-1].startswith("--")):
        source = "dir"
    else:
        source = "file"
   
    if(source == "file"):
        getProblemParams(argv[-1])
    else:
        os.chdir("problems")
        for file in glob.glob("*"):
            getProblemParams(file)
    
        os.chdir("../")
     
    if(len(argv) < 2):
        print("Program needs at least 1 arguments")
        return
    elif(argv[1] == "--all" and source == "file"):
        for solver in solvers:
            runSolver(solver, argv[-1])
        for solver in solvers:
            scanOutput(solver)
    elif(source == "file"):
        for solver in argv[1:-1]:
            item = (item for item in solvers if item["id"] == solver[2:]).__next__()
            runSolver(item, argv[-1])
            scanOutput(item)
    elif(argv[1] == "--all" and source == "dir"):
        listdir = os.listdir(script_dir + "/problems")
        for solver in solvers:
            for file in listdir:
                runSolver(solver, file)
        for solver in solvers:
            for file in listdir:
                scanOutput(solver, file)
    elif(source == "dir"):
        listdir = os.listdir(script_dir + "/problems")
        for solver in argv[1:]:
            item = (item for item in solvers if item["id"] == solver[2:]).__next__()
            for file in listdir:
                runSolver(item, file)
                scanOutput(item, file)
    
    cleanAfter(solvers)
                       
if __name__ == "__main__":
    main(sys.argv)