#!/usr/bin/python
import sys
import glob
import os
import json
import time
import re
from subprocess import call, STDOUT, Popen
import input_translator
from sys import stdout
import output_scanner

source = ""
script_dir = ""

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
        trans_cmd = "input_translator." + solver["id"] + "(\"" + file_name + "\")"
        trans_file = eval(trans_cmd)
        command = ""
        for x in solver["run"]:
            if(x == "file_name"):
                x = trans_file
            elif(x == "file_out"):
                x = solver["id"] + "." + solver["out"]
            command += x + " "
        t1 = time.time()
        Popen(command, shell=True).wait()
        t2 = time.time()
        ts = ((t2-t1)*1000).__str__()
        results.write(ts + "ms " + solver["id"] + "\n")
    else:
        command = ""
        for x in solver["run"]:
            if(x == "file_name"):
                x = script_dir + "/problems/" + file_name
            elif(x == "file_out"):
                x = script_dir + "/outputs/" + file_name + solver["id"] + "." + solver["out"]
            command += x + " "
        t1 = time.time()
        Popen(command, shell=True).wait()
        t2 = time.time()
        ts = ((t2-t1)*1000).__str__()
        results.write(ts + "ms " + solver["id"] + "\n")
        
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
            factors = re.findall(factor, line)
            for f in factors:
                ff = float(f)
                if(ff > max):
                    max = ff
                if(abs(ff) < abs(min) and abs(ff) != 0):
                    min = ff
     
    results.write("Number of variables: " + NoV.__str__() + "\n")
    results.write("Number of constraints: " + NoC.__str__() + "\n")
    CD = (NoViC.__float__() / (NoV * NoC)).__str__()
    results.write("Constraints density: " + CD + "\n")
    results.write("Maximum factor: " + max.__str__() + "\n")
    results.write("Minimum factor: " + min.__str__() + "\n")
    
    problem.close()
    results.close()
    
def scanOutput(solver):
    if(solver["id"] == "lp_solve" or solver["id"] == "glpk" or solver["id"] == "cplex"):
        scan_cmd = "output_scanner." + solver["id"] + "()"
        d = eval(scan_cmd)
        #d = output_scanner.lp_solve()
        file = open("RESULTS", 'a')
        file.write(d["VoOF"].__str__() + " Value of objective function [" + solver["id"] + "]" + "\n")
        i = 1
        for x in d["VotV"]:
            file.write(x.__str__() + " x" + i.__str__() + " [" + solver["id"] + "]\n")
            i += 1
            
def cleanResults():
    os.chdir("results")
    for file in glob.glob("*"):
        os.unlink(file)
    
    os.chdir("../")
           
def main(argv):
    solvers = getConfiguredSolvers()
    cleanResults()
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
            item = (item for item in solvers if item["id"] == solver[2:]).next()
            runSolver(item, argv[-1])
            scanOutput(solver)
    elif(argv[1] == "--all" and source == "dir"):
        return
    elif(source == "dir"):
        listdir = os.listdir(script_dir + "/problems")
        for solver in argv[1:]:
            item = (item for item in solvers if item["id"] == solver[2:]).next()
            for file in listdir:
                runSolver(item, file)
            #scanOutput(solver) 
                       
if __name__ == "__main__":
    main(sys.argv)