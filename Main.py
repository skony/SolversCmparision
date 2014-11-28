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


def getConfiguredSolvers():
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
    results = open("RESULTS", 'a')
    if(solver["input_translator"] == "true"):
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
                x = file_name
            elif(x == "file_out"):
                x = solver["id"] + "." + solver["out"]
            command += x + " "
        t1 = time.time()
        Popen(command, shell=True).wait()
        t2 = time.time()
        ts = ((t2-t1)*1000).__str__()
        results.write(ts + "ms " + solver["id"] + "\n")
        
def getProblemParams(file_path):
    problem = open(file_path, 'r')
    results = open("RESULTS", 'a')
    pattern = re.compile(".+[:]")
    NoV = 1
    NoC = 0
    NoViC = 0
    cons = False
    
    for line in problem:
        if(re.match(pattern, line) and cons==False):
            NoV += line.count('+')
            NoV += line.count('-')
            cons = True
        elif(re.match(pattern, line)):
            NoC += 1
            NoViC += line.count('+')
            NoViC += line.count('-')
            NoViC += 1
    
    results.write("Number of variables: " + NoV.__str__() + "\n")
    results.write("Number of constraints: " + NoC.__str__() + "\n")
    CD = (NoViC.__float__() / (NoV * NoC)).__str__()
    results.write("Constraints density: " + CD + "\n")
           
def main(argv):    
    solvers = getConfiguredSolvers()
    r = open("RESULTS", "w")
    r.write("")
    r.close()
    getProblemParams(argv[-1])
    
    if(len(argv) < 3):
        print("Program needs at least 2 arguments")
        return
    elif(argv[1] == "--all"):
        for solver in solvers:
            runSolver(solver, argv[-1])
    else:
        for solver in argv[1:-1]:
            item = (item for item in solvers if item["id"] == solver[2:]).next()
            runSolver(item, argv[-1])
                       
if __name__ == "__main__":
    main(sys.argv)