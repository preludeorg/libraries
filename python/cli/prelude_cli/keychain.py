import os
import configparser
from pathlib import Path
from os.path import exists


def get_creds(keychain):
    try:
        cfg = keychain.read_keychain_config()
        profile = next(s for s in cfg.sections() if s == keychain.profile)
        account = cfg.get(profile, 'account')
        token = cfg.get(profile, 'token')
        hq = cfg.get(profile, 'hq')
        return account, token, hq
    except FileNotFoundError:
        raise Exception('Please create a %s file' % keychain.keychain_location)
    except KeyError as e:
        raise Exception('Property not found, %s' % e)
    except StopIteration:
        raise Exception('Could not find "%s" profile in %s' % (keychain.profile, keychain.keychain_location))


class Keychain:

    def __init__(self, profile='default', hq='https://api.preludesecurity.com', keychain_location=os.path.join(Path.home(), '.prelude', 'keychain.ini')):
        self.profile = profile
        self.hq = hq
        self.keychain_location = keychain_location

    def configure(self, account_id, token, hq='https://api.preludesecurity.com', profile='default'):
        cfg = self._merge_configs(self.read_keychain_config(hq, profile), self.generate_config(account_id, token, hq, profile))
        self.write_keychain_config(cfg=cfg)

    def read_keychain_config(self, hq='https://api.preludesecurity.com', profile='default'):
        if not exists(self.keychain_location):
            head, _ = os.path.split(Path(self.keychain_location))
            Path(head).mkdir(parents=True, exist_ok=True)
            open(self.keychain_location, 'x').close()
            self.configure('', '', hq, profile)
        cfg = configparser.ConfigParser()
        cfg.read(self.keychain_location)
        return cfg

    def write_keychain_config(self, cfg):
        with open(self.keychain_location, 'w') as f:
            cfg.write(f)

    @staticmethod
    def generate_config(account_id, token, hq, profile):
        cfg = configparser.ConfigParser()
        cfg[profile] = {
            'hq': hq,
            'account': account_id,
            'token': token
        }
        return cfg

    @staticmethod
    def _merge_configs(cfg_from, cfg_to):
        for section in cfg_from.sections():
            if section not in cfg_to:
                cfg_to[section] = {k: cfg_from[section][k] for k in cfg_from[section]}
        return cfg_to
