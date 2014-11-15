#!/usr/bin/python
import sys
import glob
import os
import json
#from pprint import pprint
from subprocess import call
import input_translator

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
    
def runAllSolvers():
    return 0
    
def runSolver(solver, file_name):
    if(solver["input_translator"] == "true"):
        command = "input_translator." + solver["id"] + "(\"" + file_name + "\")"
        #input_translator.lp_solve(file_name)
        trans_file = eval(command)
    else:
        call([solver["run"], solver["args"], file_name, "--output", "file.out"])
    
def main(argv):    
    solvers = getConfiguredSolvers()
    
    if(len(argv) < 3):
        print("Program needs at least 2 arguments")
        return
    elif(argv[1] == "--all"):
        runAllSolvers()
    else:
        for solver in argv[1:-1]:
            item = (item for item in solvers if item["id"] == solver[2:]).next()
            runSolver(item, argv[-1])
                       
if __name__ == "__main__":
    main(sys.argv)