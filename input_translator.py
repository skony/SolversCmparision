import re

def lp_solve(file):
    base_file = open(file, 'r')
    new_file = open("lp_solve_problem.lp", 'w')
    pattern = re.compile(".+[:]")
    general = False
    
    for line in base_file:
        if(general and line.lower().strip() != "end"):
            new_file.write(line[:-1] + ";\n")
            general = False
        elif(line.lower() == 'maximize\n' or line.lower() == 'maximum\n' or line.lower() == 'max\n'):
            new_file.write("max")
        elif(re.match(pattern, line) ):
            new_file.write(line.rsplit(':', -1)[1][:-1] + ";\n")
        elif(line.lower().strip() == "subject to" or line.lower().strip() == "bounds" or line.lower().strip() == "end"):
            new_file.write("")
        elif(line.lower().strip() == "general"):
            new_file.write("int ")
            general = True
        elif(len(line.strip()) > 1): 
            if(line.strip()[-2] != ';' ):
                new_file.write(line[:-1] + ";\n")
        else:
            new_file.write(line)
            
    base_file.close()
    new_file.close()
    return "lp_solve_problem.lp"   
    