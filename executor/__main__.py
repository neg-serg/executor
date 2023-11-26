#!/usr/bin/python
import asyncio
from sys import argv
import inotify
import inotify.adapters
from threading import Thread
from executor.executor import Executor, MsgBroker

def config_watch():
    i=inotify.adapters.Inotify()
    i.add_watch(executor.config.dir())
    for event in i.event_gen(yield_nones=False):
        if event is None:
            return
        (_, type_names, _, _) = event
        if type_names == ['IN_CLOSE_WRITE']:
            executor.reload()

if __name__ == '__main__':
    loop=asyncio.new_event_loop()
    executor = Executor()
    cmd = ''
    if len(argv) >= 2: # should have cmd at least
        cmd = argv[1]
        if cmd == 'daemon':
            port = 15556
            Thread(target=config_watch,daemon=True).start()
            MsgBroker.mainloop(loop, executor, port)
    for arg in argv[2:]:
        if cmd == 'config' or cmd == 'cfg':
            print(executor.cfg[arg])
        if cmd == 'run' or cmd == 'prog':
            executor.run(arg)
