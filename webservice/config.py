# -*- coding: utf-8 -*-
import yaml


def _default_conf():
    import os
    return os.path.join(os.path.dirname(__file__), 'config.yaml')


class DBConfig:
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = _default_conf()
        self._conf = yaml.load(open(config_file, "r"))

    def get(self, path):
        """
        :param path: data.source
        :return:
        """
        elements = path.split('.')
        conf = self._conf
        for i in range(len(elements)):
            conf = conf[elements[i]]
        return conf


class DevelopConfig:
    DEBUG = True
    MONGO_URI = 'mongodb://192.168.10.152:27017/test'
    MONGO_CONNECT = False
    CELERY_BROKER_URL = 'redis://localhost/15'


class ProductionConfig:
    DEBUG = False
    MONGO_CONNECT = False