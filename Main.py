#!/usr/bin/python
import glob
import json
import os
import re
import shlex
from signal import SIGTERM
import bisect
import subprocess
import sys
import time

import Charts
import input_translator


source = ""
script_dir = ""
outputs_dir = ""
problems_dir = ""
results_dir = ""
charts_dir = ""
variables_dir = ""
timeout_problems = []

def bi_contains(lst, item):
    return (item <= lst[-1]) and (lst[bisect.bisect_left(lst, item)] == item)

def getConfiguredSolvers():
    global script_dir
    solvers = []
#     script_dir = os.path.dirname(__file__)
    os.chdir("solvers")
    
    for file in glob.glob("*.json"):
        abs_path = script_dir + "/solvers/" + file
        json_file = open(abs_path)
        data = json.load(json_file)
        solvers.append(data)
        json_file.close()
    
    os.chdir("../")
    return solvers

#mode: time console    
def runSolver(solver, file_name, mode, deadline):
    results = open(script_dir + "/results/" + file_name + "RESULTS", 'a')
    if(solver["input"] != "lp_solve"):
        trans_cmd = "input_translator." + solver["input"] + "(\"" + script_dir + "/problems/" + file_name + "\")"
        problem_file = eval(trans_cmd)
    else:
        problem_file = script_dir + "/problems/" + file_name
        
    file_out_path = script_dir + "/outputs/" + file_name + solver["id"] + "." + solver["out"]
    if mode == "time":
        file_out = open(file_out_path, 'w')
    elif mode == "console":
        file_out = None
    stdout = None
    
    my_env = os.environ.copy()
    if "env" in solver:
        for env in solver["env"].keys():
            my_env[env] = solver["env"][env]
    
    command = ""
    if mode == "time" or "run_console" not in solver:
        run = solver["run"]
    elif "run_console" in solver and mode == "console":
        run = solver["run_console"]
    for x in run:
        if(x == "file_name"):
            x = problem_file
        elif(x == ">"):
            stdout = file_out
            break
        elif(x == "<"):
            stdout = file_out
            continue
        elif("file_out" in x):
            x = x.replace("file_out", file_out_path)
        command += x + " "
    if mode == "time":
        t1 = time.time()
        try:
            p = subprocess.Popen(shlex.split(command), stdout=stdout, env=my_env)       
            p.wait(timeout = float(deadline))
            t2 = time.time()
            ts = ((t2-t1)*1000).__str__()
            results.write(ts + "ms " + solver["id"] + "\n")
        except subprocess.TimeoutExpired:
            os.kill(p.pid, SIGTERM)
            t2 = time.time()
            ts = ((t2-t1)*1000).__str__()
            results.write(ts + "ms TIMEOUT_EXCEPTION " + solver["id"] + "\n")
            timeout_problems.append(file_name + solver["id"])
    elif mode == "console":
        if file_name + solver["id"] not in timeout_problems:
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
            p = subprocess.Popen(shlex.split(command), stdout=stdout, stderr=stderr, env=my_env)
            console, err = p.communicate()
            print(console)
            print(err)
            if "exceptions" in solver:
                for exc in solver["exceptions"].keys():    
                    if solver["exceptions"][exc] in console.__str__() or solver["exceptions"][exc] in err.__str__():
                        results.write(exc.upper() + "_EXCEPTION [" + solver["id"] + "]\n")
                        
    results.close()
    if file_out != None:
        file_out.close()
        
def getProblemParams(file_path):
    problem = open(file_path, 'r')
    os.chdir("../")
    os.chdir("results")
    results = open(file_path + "RESULTS", 'a')
    os.chdir("../")
    os.chdir("problems")
    var_pattern = re.compile("[A-Za-z]+[\w.]*")
    NoV = 0
    NoC = 0
    NoViC = 0
    cons = False
    bounds = False
    max = 1
    min = 1
    factor = re.compile("[\+\-\s][0-9]+[.]{0,1}[0-9]*")
    found_vars = []
     
    for line in problem:
        if((re.match("min:", line) or re.match("max:", line)) and cons==False):
            cons = True
            factors = re.findall(factor, line)
            for f in factors:
                ff = float(f)
                if(ff > max):
                    max = ff
                if(abs(ff) < abs(min) and abs(ff) != 0):
                    min = ff
            for var in re.findall(var_pattern, line):
                bisect.insort_left(found_vars, var)
                NoV += 1
                NoViC += 1
        elif cons and not bounds:
            factors = re.findall(factor, line)
            for f in factors:
                ff = float(f)
                if(ff > max):
                    max = ff
                if(abs(ff) < abs(min) and abs(ff) != 0):
                    min = ff
            vars = re.findall(var_pattern, line)
            if len(vars) < 2:
                bounds = True
            else:
                NoC += 1
                if ':' in line:
                    vars = vars[1:]    #name of constrainst not included
                for var in vars:   
                    if not bi_contains(found_vars, var):
                        bisect.insort_left(found_vars, var)
                        NoV += 1
                        NoViC += 1
                    else:
                        NoViC += 1
        elif bounds:
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
        file2 = open(results_dir + problem + "RESULTS", 'a')
        file2.write("-0.0 Value of objective function EXCEPTION [" + solver["id"] + "]" + "\n")
        return
    
    VoOF = -0.0
    VotV = {}
    pattern = re.compile("[-+ ]?[0-9]+[.]?[0-9]*e?[+-]?[0-9]*")
    var_pattern = re.compile("[-+ ]?[0-9]+[.]?[0-9]*e?[+-]?[0-9]*")
    var_name_pattern = re.compile("[a-zA-Z]+\w*")
    if(solver["VotV_on"] == "false"):   #searching values of the variables disabled
        for line in file:
            if(re.search(solver["VoOF"], line) != None):
                list = re.findall(pattern, line)
                if(len(list) > 0):
                    try:
                        VoOF = float(list[0])
                    except ValueError:
                        None
    elif(solver["VotV_on"] == "true"):  #searching values of the variables enabled
        VotV_started = False
        VotV_begin = False
        VotV_line = 0
        try:
            for line in file:
                if(re.search(solver["VoOF"], line) != None):
                    list = re.findall(pattern, line)
                    if(len(list) > 0):
                        try:
                            VoOF = float(list[0])
                        except ValueError:
                            None
                     
                if(VotV_started == True):   #section with variables started
                    if(re.search(solver["VotV_stop"], line) != None and solver["VotV_stop"] != ""):
                        VotV_started = False
                        break
                    list = re.findall(var_pattern, line)
                    if(solver["VotV"] != ""):
                        name_list = re.findall(var_name_pattern, line.rsplit(solver["VotV"], -1)[1])
                    else:
                        name_list = re.findall(var_name_pattern, line)
                    if(len(name_list) > 0):
                        VotV[name_list[0]] = -0.0
                    else:
                        VotV_started = False
                        break
                    if(len(list) >= solver["VotV_num"]):
                        try:
                            VotV[name_list[0]] = float(list[solver["VotV_num"]-1])
                        except ValueError:
                            VotV[name_list[0]] = -0.0
                elif(VotV_begin == True):   #
                    if(re.search(solver["VotV_start"][VotV_line], line) != None):
                        if(len(solver["VotV_start"]) == VotV_line+1):
                            VotV_started = True
                        else:
                            VotV_line += 1  
                elif(re.search(solver["VotV_start"][0], line) != None):
                    if(len(solver["VotV_start"]) == 1):
                        VotV_started = True
                    elif(len(solver["VotV_start"]) > 1):
                        VotV_begin = True
                        VotV_line += 1
        except OSError:
            VotV = {}
                
    file2 = open(results_dir + problem + "RESULTS", 'a')
    if(VoOF != -0.0):
        file2.write(VoOF.__str__() + " Value of objective function [" + solver["id"] + "]" + "\n")
    else:
        file2.write(VoOF.__str__() + " Value of objective function EXCEPTION [" + solver["id"] + "]" + "\n")
    if(solver["VotV_on"] == "true"):
        file3 = open(variables_dir + problem + "VARIABLES", 'a')
        file3.write("*** " + solver["id"].upper() + " VALUES OF THE VARIABLES:\n")
        for var in VotV.keys():
            file3.write(var + " " + VotV[var].__str__() + "\n")
        file3.close()
    file.close()
    file2.close()
            
def cleanBefore(solvers):
    os.chdir(results_dir)
    for file in glob.glob("*"):
        os.unlink(file)
        
    os.chdir(outputs_dir)
    for file in glob.glob("*"):
        os.unlink(file)
    
    os.chdir(variables_dir)
    for file in glob.glob("*"):
        os.unlink(file)
    
    os.chdir(charts_dir)
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
    os.chdir(results_dir)
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
    global charts_dir
    global variables_dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(script_dir)
    outputs_dir = script_dir + "/outputs/"
    problems_dir = script_dir + "/problems/"
    results_dir = script_dir + "/results/"
    charts_dir = script_dir + "/charts/"
    variables_dir = script_dir + "/variables/"
    
    solvers = getConfiguredSolvers()
    cleanBefore(solvers)
    global source
    
    os.chdir("problems")
    for file in glob.glob("*"):
        getProblemParams(file)
     
    os.chdir("../")
         
    if(len(argv) < 4):
        print("Program needs at least 3 arguments")
        return

    if(argv[1] == "--all"):
        listdir = os.listdir(script_dir + "/problems")
        for solver in solvers:
            for file in listdir:
                runSolver(solver, file, "time", argv[-1])
        for solver in solvers:
            for file in listdir:
                runSolver(solver, file, "console", argv[-1])
        for solver in solvers:
            for file in listdir:
                scanOutput(solver, file)
    else:
        listdir = os.listdir(script_dir + "/problems")
        for solver in argv[1:-2]:
            item = (item for item in solvers if item["id"] == solver[2:]).__next__()
            for file in listdir:
                runSolver(item, file, "time", argv[-1])
                runSolver(item, file, "console", argv[-1])
                scanOutput(item, file)
                
    cleanAfter(solvers)
    Charts.drawBarChart(solvers, results_dir, charts_dir)
    Charts.drawLineChart(solvers, results_dir, charts_dir, "variables")
    Charts.drawLineChart(solvers, results_dir, charts_dir, "constraints")
    Charts.drawLineChart(solvers, results_dir, charts_dir, "density")
    Charts.drawLineChart(solvers, results_dir, charts_dir, "factors")
    Charts.drawLineChart(solvers, results_dir, charts_dir, "multiplication")
    Charts.drawLineChart(solvers, results_dir, charts_dir, "variables", True)
    Charts.drawLineChart(solvers, results_dir, charts_dir, "constraints", True)
    Charts.drawLineChart(solvers, results_dir, charts_dir, "density", True)
    Charts.drawLineChart(solvers, results_dir, charts_dir, "factors", True)
    Charts.drawLineChart(solvers, results_dir, charts_dir, "multiplication", True)
    Charts.checkIfCorrect(solvers, variables_dir, problems_dir, results_dir)
    Charts.drawLineChart(solvers, results_dir, charts_dir, "miscount")
    Charts.drawLineChart(solvers, results_dir, charts_dir, "miscount", True)
                       
if __name__ == "__main__":
    main(sys.argv)