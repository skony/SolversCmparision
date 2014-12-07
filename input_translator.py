import re
import os

def cplex(file):
    base_file = open(file, 'r')
    new_file = open(file + "cplex.lp", 'w')
    constrait = re.compile("\w+:")
    bound = re.compile("\w+")
    
    for line in base_file:
        if(re.match("min:", line)):
            new_file.write("Minimize\n")
            new_file.write("obj:" + line.rsplit(":",-1)[1][:-2] + "\n")
            new_file.write("Subject To\n")
        elif(constrait.match(line) != None):
            new_file.write(line[:-2].replace('<', '<=').replace('>', '>=') + "\n" )
        elif(bound.match(line) != None):
            new_file.write(line[:-2].replace('<', '<=').replace('>', '>=') + "\n" )
    
    new_file.write("End") 
    base_file.close()
    new_file.close()
    return file + "cplex.lp"
   
def cmd(file_path):
    file = cplex(file_path)
    head, tail = os.path.split(file)
    head2, tail2 = os.path.split(head)
    new_file = open(file[:-3] + "cmd", 'w')
    new_file.write("read " + file + " lp\n")
    new_file.write("opt\n")
    new_file.write("write " + head2 + "/outputs/" + tail[:-3] + ".sol\n")
    new_file.write("y\n")
    new_file.write("quit\n")
    new_file.write("\n")
    return file[:-3] + "cmd"
        
    