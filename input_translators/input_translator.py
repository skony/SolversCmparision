def lp_solve(file):
    base_file = open(file, 'r')
    new_file = open("lp_solve_problem.lp", 'w')   
    for line in base_file:
        print line
        new_file.write(line)
        #if any(line in s for s in ['MAXIMIZE'])