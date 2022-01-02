import inspect
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Union
from pathlib import Path
from configparser import ConfigParser

DEFAULT_CONF = """

"""

class ConfigException(Exception):
    pass

class ConfigSection(metaclass=ABCMeta):

    @property
    @abstractmethod
    def defaults(self) -> dict:
        pass

    @classmethod
    def from_dict(cls, conf_dict:dict) -> 'ConfigSection':
        conf = dict(cls.defaults(cls), **conf_dict)
        data = {key: cls._val(cls, conf, key, val) for key, val in inspect.signature(cls).parameters.items()}
        return cls(**data)

    def _val(self, conf_dict:dict, key:str, val:inspect.Parameter) -> any:
        return conf_dict.get(key) if val.default == val.empty else conf_dict.get(key, val.default)


@dataclass
class Config(metaclass=ABCMeta):
    @property
    @abstractmethod
    def defaults(self) -> dict:
        pass

    @classmethod
    def from_config_file(cls: 'Config', config_file: Union[str, Path], write_default: bool = False) -> 'Config':
        config_file = config_file if isinstance(config_file, Path) else Path(config_file)
        if not config_file.exists():
            if write_default:
                cls.write_configuration(config_file)
            else:
                raise ConfigException('File not found!')

        parser: ConfigParser = cls.read_configuration(config_file)
        return cls.from_dict(parser._sections)

    
    @classmethod
    def from_dict(cls: 'Config', conf_dict: dict) -> 'Config':
        conf = dict(cls.defaults(cls), **conf_dict)
        data = {key: val.annotation.from_dict(cls._val(cls, conf, key, val)) for key, val in inspect.signature(cls).parameters.items()}
        return cls(**data)

    def write_configuration(file: Path) -> None:
        with file.open('w', encoding='utf-8') as f:
            f.write(DEFAULT_CONF)

    def read_configuration(file: Path) -> ConfigParser:
        parser = ConfigParser()
        with file.open('r', encoding='utf-8') as f:
            parser.read_file(f)
        return parser

    def _val(self, conf_dict:dict, key:str, val:inspect.Parameter) -> any:
        return conf_dict.get(key) if val.default == val.empty else conf_dict.get(key, val.default)

