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
        self.config_dir=config_dir
        self.cfg_path=f'{config_dir}/{self.mod}.yml'
        if os.path.isfile(self.cfg_path) and os.stat(self.cfg_path).st_size > 0:
            self.cfg={}
            self.load_config() # load current config
        else:
            logging.error(f'There is no config file in {self.cfg_path}, exit')
            quit()


    def dir(self) -> str:
        """ Return config dir """
        return self.config_dir

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

    def reload(self, mod, *_) -> str:
        """ Reload config for current selected module. Call load_config, print
        debug messages and reinit all stuff. """
        prev_conf=self.cfg
        ret=''
        try:
            self.load_config()
            mod.__init__()
            ret=f"[{self.mod}] config reloaded"
            logging.info(ret)
            print(ret)
            return ret
        except Exception:
            ret=f"[{self.mod}] config reload failed"
            logging.info(ret)
            self.cfg=prev_conf
            mod.__init__(*_)
            return ret
    
    def load_config(self) -> None:
        """ Load config """
        try:
            y=yaml.YAML(typ='rt')
            with open(self.cfg_path, "rb") as mod_cfg:
                self.cfg=y.load(mod_cfg)
        except FileNotFoundError:
            logging.error(f'file {self.cfg_path} not exists')
