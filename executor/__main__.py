#!/usr/bin/python
from sys import argv
from executor.executor import Executor

if __name__ == '__main__':
    executor = Executor()
    cmd = ''
    if len(argv) >= 3: # cmd and parameter
        cmd = argv[1]
    for arg in argv[2:]:
        if cmd == 'config' or cmd == 'cfg':
            print(executor.cfg[arg])
        if cmd == 'run' or cmd == 'prog':
            executor.run(arg)
