#!/usr/bin/python
import sys
import glob
import os
import json
#from pprint import pprint
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
        Popen(command, shell=True)
    else:
        command = ""
        for x in solver["run"]:
            if(x == "file_name"):
                x = file_name
            elif(x == "file_out"):
                x = solver["id"] + "." + solver["out"]
            command += x + " "
        Popen(command, shell=True)
    
def main(argv):    
    solvers = getConfiguredSolvers()
    
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