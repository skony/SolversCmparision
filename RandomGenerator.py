'''
Created on 7 sty 2015

@author: piotrek
'''
import sys

def chunks(l, n):
    if n < 1:
        n = 1
    return [l[i:i + n] for i in range(0, len(l), n)]

def generator(argv):
    max_n = min_n = max_m = min_m = max_f = min_f = 0
    max_g = min_g = 0.0
    
    if(len(argv) != 13):
        print("Program needs exactly 12 arguments")
        return
    
    parsed_args = chunks(argv[1:], 3)
    for args in parsed_args:
        if(args[0] == '-n'):
            min_n = args[1]
            max_n = args[2] 
        elif(args[0] == '-m'):
            min_m = args[1]
            max_m = args[2]
        elif(args[0] == '-f'):
            min_f = args[1]
            max_f = args[2]
        elif(args[0] == '-g'):
            min_g = args[1]
            max_g = args[2]
    
if __name__ == "__main__":
    generator(sys.argv)