#!/usr/bin/python
import asyncio
from sys import argv
from executor.executor import Executor, MsgBroker

def main(loop):
    executor = Executor()
    cmd = ''
    if len(argv) >= 2: # should have cmd at least
        cmd = argv[1]
        if cmd == 'daemon':
            port = 15556
            MsgBroker.mainloop(loop, executor, port)
    for arg in argv[2:]:
        if cmd in {'config', 'cfg'}:
            print(executor.cfg[arg])
        elif cmd in {'run', 'prog'}:
            executor.run(arg)

if __name__ == '__main__':
    loop=asyncio.new_event_loop()
    main(loop)
    loop.close()
