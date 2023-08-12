#!/usr/bin/python
import asyncio
from sys import argv
from executor.executor import Executor, MsgBroker

if __name__ == '__main__':
    loop=asyncio.new_event_loop()
    executor = Executor()
    cmd = ''
    if len(argv) >= 2: # should have cmd at least
        cmd = argv[1]
        if cmd == 'daemon':
            port = 15556
            MsgBroker.mainloop(loop, executor, port)
    for arg in argv[2:]:
        if cmd == 'config' or cmd == 'cfg':
            print(executor.cfg[arg])
        if cmd == 'run' or cmd == 'prog':
            executor.run(arg)
