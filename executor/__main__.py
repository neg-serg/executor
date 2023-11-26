#!/usr/bin/python
import asyncio
from sys import argv
import inotify
import inotify.adapters
from threading import Thread
from executor.executor import Executor, MsgBroker

EXECUTOR_PORT=15556

def config_watch():
    i=inotify.adapters.Inotify()
    i.add_watch(executor.config.dir())
    for event in i.event_gen(yield_nones=False):
        if event is None:
            return
        (_, type_names, _, _)=event
        if type_names == ['IN_CLOSE_WRITE']:
            executor.reload()

if __name__ == '__main__':
    loop=asyncio.new_event_loop()
    executor=Executor()
    cmd=''
    if len(argv) >= 2: # should have cmd at least
        cmd=argv[1]
        if cmd == 'daemon':
            Thread(target=config_watch,daemon=True).start()
            MsgBroker.mainloop(loop, executor, EXECUTOR_PORT)
    for arg in argv[2:]:
        if cmd in {'config','cfg'}:
            print(executor.cfg[arg])
        if cmd in {'run','prog'}:
            executor.run(arg)
