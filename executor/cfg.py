import os
import logging
import errno
import ruamel.yaml as yaml

class cfg():
    def __init__(self) -> None:
        self.mod='executor'    # detect current extension
        xdg_home=os.environ.get('XDG_CONFIG_HOME', '')
        config_dir=f'{xdg_home}/{self.mod}'
        if not xdg_home:
            logging.error('XDG_CONFIG_HOME is not set')
            quit()
        else:
            cfg.create_dir(config_dir)
        self.cfg_path=f'{config_dir}/{self.mod}.yml'
        if os.path.isfile(self.cfg_path) and os.stat(self.cfg_path).st_size > 0:
            self.cfg={}
            self.load_config() # load current config
        else:
            logging.error(f'There is no config file in {self.cfg_path}, exit')
            quit()

    @staticmethod
    def create_dir(dirname) -> None:
        ''' Helper function to create directory
            dirname(str): directory name to create '''
        if os.path.isdir(dirname):
            return
        try:
            logging.info(f'Creating dir {dirname}')
            os.makedirs(dirname)
        except OSError as oserr:
            if oserr.errno != errno.EEXIST:
                raise

    def load_config(self) -> None:
        """ Reload config """
        try:
            with open(self.cfg_path, "rb") as mod_cfg:
                self.cfg=yaml.load(mod_cfg, Loader=yaml.CLoader)
        except FileNotFoundError:
            logging.error(f'file {self.cfg_path} not exists')
