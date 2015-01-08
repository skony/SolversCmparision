'''
Created on 7 sty 2015

@author: piotrek
'''
import sys
import os
from random import randint, random, uniform, choice, sample
from math import floor

def getFactor(max_f):
    if(max_f > 0):
        max = 9.99 * (max_f + 1)
    
    return round(uniform(0.0, max), 2)

def chunks(l, n):
    if n < 1:       
        n = 1
    return [l[i:i + n] for i in range(0, len(l), n)]

def generator(argv):
    max_n = min_n = max_m = min_m = max_f = min_f = min_x = max_x = 0
    max_g = min_g = 0.0
    
    if(len(argv) != 16):
        print("Program needs exactly 15 arguments")
        return
    
    parsed_args = chunks(argv[1:], 3)
    for args in parsed_args:
        if(args[0] == '-n'):
            min_n = int(args[1])
            max_n = int(args[2]) 
        elif(args[0] == '-m'):
            min_m = int(args[1])
            max_m = int(args[2])
        elif(args[0] == '-f'):
            min_f = int(args[1])
            max_f = int(args[2])
        elif(args[0] == '-g'):
            min_g = float(args[1])
            max_g = float(args[2])
        elif(args[0] == '-x'):
            min_x = int(args[1])
            max_x = int(args[2])
          
    problems_dir = os.path.dirname(__file__)  + "/problems/"
            
    x = randint(min_x, max_x)
    for i in range(x):
        problem = ''.join(choice('0123456789ABCDEFGHIJKLMNOPRSTUWQYXZW') for i in range(8))
        n = randint(min_n, max_n)
        m = randint(min_m, max_m)
        f = max_f
        g = uniform(min_g, max_g)
        
        file = open(problems_dir + problem, 'w')
        file.write("max: ")
        for j in range(n):
            file.write("+" + getFactor(f).__str__() + " X" + j.__str__() + " ")
        file.write(";\n")
        F = floor(m * n * g)
        non_empty = sample(range(1, m * n), F)
        index = [0] * (m * n)
        for j in non_empty:
            index[j] = 1
        pos = 1
        for j in range(m):
            const_start = False
            for k in range(n):
                if pos in non_empty:
                    if(const_start):
                        file.write("+" + getFactor(f).__str__() + " X" + k.__str__() + " ")
                    else:
                        file.write("C" + j.__str__() + ": +" + getFactor(f).__str__() + " X" + k.__str__() + " ")
                        const_start = True
                pos += 1
            if(const_start):
                file.write("<= " + getFactor(f).__str__() + ";\n")
        file.close()    
    
if __name__ == "__main__":
    generator(sys.argv)