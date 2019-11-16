import logging, coloredlogs, colorama
import logging.config
import yaml

from enum import Enum, auto

from .file_io import get_path

import os

DEFAULT_LOGGER_CONFIG_FILE = 'logging.conf'
DEFAULT_LOGGER_CONFIG_FILE_PATH = get_path(__file__, DEFAULT_LOGGER_CONFIG_FILE)

class LoggerTypes(Enum):
    DEVELOP = auto()
    RELEASE = auto()

    def __str__(self):
        mapping = {
            self.DEVELOP.value: 'develop',
            self.RELEASE.value: 'release'
        }

        return mapping.get(self.value)

class Logger():
    def __init__(self, config_file_path=DEFAULT_LOGGER_CONFIG_FILE_PATH):
        self._config = None
        
        colorama.init()
        
        if not os.path.isfile(config_file_path):
            raise FileNotFoundError(config_file_path)
        
        with open(config_file_path, 'r') as config:
            self._config = yaml.safe_load(config.read())
            logging.config.dictConfig(self._config)
    
    @staticmethod
    def get(type: LoggerTypes, config_file_path=DEFAULT_LOGGER_CONFIG_FILE_PATH) -> logging.Logger:
        logger = Logger(config_file_path)
        return logging.getLogger(str(type))