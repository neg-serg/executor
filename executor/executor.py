''' Terminal manager. Give simple and consistent way for user to create tmux
sessions on dedicated sockets. Also it can run simply run applications without
Tmux. The main advantage is dynamic config reloading and simplicity of adding
or modifing of various parameters, also it works is faster then dedicated
scripts, because there is no parsing / translation phase here in runtime. '''

from sys import argv
from threading import Thread
from typing import List
import asyncio
import inotify
import inotify.adapters
import logging
import shlex
import subprocess

from executor.execenv import execenv as env
from executor.cfg import cfg

class extension():
    def __init__(self):
        pass

    def send_msg(self, args: List):
        """ Creates bindings from socket IPC to current module public function
        calls. This function defines bindings to the module methods that can be
        used by external users as i3-bindings, etc. Need the [send] binary
        which can send commands to the appropriate socket.
        args (List): argument list for the selected function. """
        return getattr(self, args[0])(*args[1:])

class MsgBroker():
    lock=asyncio.Lock()

    @classmethod
    def mainloop(cls, loop, mod, port) -> None:
        """ Mainloop by loop create task """
        cls.mod=mod
        loop.create_task(asyncio.start_server(
            cls.handle_client, 'localhost', port))
        loop.run_forever()

    @classmethod
    async def handle_client(cls, reader, writer) -> None:
        """ Proceed client message here """
        async with cls.lock:
            while True:
                response=(await reader.readline()).decode('utf8').split()
                if not response:
                    return
                ret=cls.mod.send_msg(response)
                if ret:
                    writer.write(bytes(f'{ret}\n', 'utf-8'))
                    await writer.drain()
                    writer.close()
                    await writer.wait_closed()
                    

class Executor(extension):
    ''' Terminal manager. Easy and consistent way to create tmux sessions on dedicated sockets. The main advantage is dynamic config
    reloading and simplicity of adding or modifing of various parameters. '''
    def __init__(self) -> None:
        log=logging.getLogger()
        log.setLevel(logging.INFO)
        self.envs={}
        self.config=cfg()
        self.cfg=self.config.cfg
        self.envs={}
        for app in self.cfg:
            self.envs[app]=env(app, self.cfg)

    def __exit__(self) -> None:
        self.envs.clear()

    def reload(self) -> str:
        return str(self.config.reload(self))

    @staticmethod
    def print_exec(s) -> None:
        print(s)

    @staticmethod
    def detect_session_bind(name) -> str:
        ''' Find target session for given socket. '''
        session_list=subprocess.run(
            shlex.split(f'tmux -S {env.tmux_socket_path(name)} list-sessions'),
            stdout=subprocess.PIPE,
            check=False
        ).stdout
        return subprocess.run(
            shlex.split(f"awk -F ':' '/{name}/ {{print $1}}'"),
            stdout=subprocess.PIPE,
            input=(session_list),
            check=False
        ).stdout.decode()

    def tmux_attach(self) -> str:
        ''' Run tmux to attach to given socket. '''
        name=self.env.name
        cmd=f"{self.env.opts}" \
            f" {self.env.shell()} -i -c" \
            f" \'{env.tmux_session_attach(name)}\'"
        return cmd

    def tmux_create_session(self) -> str:
        ''' Run tmux to create the new session on given socket. '''
        exec_cmd=''
        for pos, token in enumerate(self.env.exec_tmux):
            if 0 == pos:
                exec_cmd += f'-n {token[0]} {token[1]}\\; '
            else:
                exec_cmd += f'neww -n {token[0]} {token[1]}\\; '
        if not self.env.cfg_block().get('statusline', 1):
            exec_cmd += 'set status off\\; '
        name=self.env.name
        cmd=f"{self.env.opts}" + \
            f" {self.env.shell()} -i -c" \
            f" \'{env.tmux_new_session(self.env.name)}" + \
            f" {exec_cmd} && {env.tmux_session_attach(name)}\'"
        return cmd

    def run(self, name):
        cmd=self.create_cmd(name)
        return cmd

    def create_cmd(self, name: str) -> str:
        ''' Entry point, run application with Tmux on dedicated socket(in most
        cases), or without tmux, exec_tmux is empty.
        name (str): target application name, taken from config file '''
        self.env=self.envs[name]
        if self.env.exec_tmux:
            env.prepare_tmux()
            if self.env.name in self.detect_session_bind(self.env.name):
                import i3ipc
                if not i3ipc.Connection().get_tree().find_classed(self.env.wclass):
                    return self.tmux_attach()
            else:
                return self.tmux_create_session()
        else:
            cmd=f'{self.env.opts} {self.env.exec}'
            return cmd
        return ''

    def main():
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

        # loop=asyncio.new_event_loop()
        # executor=Executor()
        # cmd=''
        # if len(argv) >= 2: # should have cmd at least
        #     cmd=argv[1]
        #     if cmd == 'daemon':
        #         Thread(target=config_watch,daemon=True).start()
        #         MsgBroker.mainloop(loop, executor, EXECUTOR_PORT)
        # for arg in argv[2:]:
        #     if cmd in {'config','cfg'}:
        #         print(executor.cfg[arg])
        #     if cmd in {'run','prog'}:
        #         executor.run(arg)
                
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
