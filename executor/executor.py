''' Terminal manager. Give simple and consistent way for user to create tmux
sessions on dedicated sockets. Also it can run simply run applications without
Tmux. The main advantage is dynamic config reloading and simplicity of adding
or modifing of various parameters, also it works is faster then dedicated
scripts, because there is no parsing / translation phase here in runtime. '''

import subprocess
import shlex
from executor.execenv import execenv as env
from executor.cfg import cfg

class Executor():
    ''' Terminal manager. Easy and consistent way to create tmux sessions on dedicated sockets. The main advantage is dynamic config
    reloading and simplicity of adding or modifing of various parameters. '''
    def __init__(self) -> None:
        self.envs = {}
        self.cfg = cfg().cfg
        self.envs = {}
        for app in self.cfg:
            self.envs[app] = env(app, self.cfg)

    def __exit__(self) -> None:
        self.envs.clear()

    @staticmethod
    def print_exec(s) -> None:
        print(s)

    @staticmethod
    def detect_session_bind(name) -> str:
        ''' Find target session for given socket. '''
        session_list = subprocess.run(
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

    def tmux_attach(self) -> None:
        ''' Run tmux to attach to given socket. '''
        name = self.env.name
        cmd = f"{self.env.opts}" \
            f" {self.env.shell()} -i -c" \
            f" \'{env.tmux_session_attach(name)}\'"
        Executor.print_exec(cmd)

    def tmux_create_session(self) -> None:
        ''' Run tmux to create the new session on given socket. '''
        exec_cmd = ''
        for pos, token in enumerate(self.env.exec_tmux):
            if 0 == pos:
                exec_cmd += f'-n {token[0]} {token[1]}\\; '
            else:
                exec_cmd += f'neww -n {token[0]} {token[1]}\\; '
        if not self.env.cfg_block().get('statusline', 1):
            exec_cmd += 'set status off\\; '
        name = self.env.name
        cmd = f"{self.env.opts}" + \
            f" {self.env.shell()} -i -c" \
            f" \'{env.tmux_new_session(self.env.name)}" + \
            f" {exec_cmd} && {env.tmux_session_attach(name)}\'"
        Executor.print_exec(cmd)

    def run(self, name: str) -> None:
        ''' Entry point, run application with Tmux on dedicated socket(in most
        cases), or without tmux, exec_tmux is empty.
        name (str): target application name, taken from config file '''
        self.env = self.envs[name]
        if self.env.exec_tmux:
            env.prepare_tmux()
            if self.env.name in self.detect_session_bind(self.env.name):
                import i3ipc
                if not i3ipc.Connection().get_tree().find_classed(self.env.wclass):
                    self.tmux_attach()
            else:
                self.tmux_create_session()
        else:
            cmd = f'{self.env.opts} {self.env.exec}'
            Executor.print_exec(cmd)
