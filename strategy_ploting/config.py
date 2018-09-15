import yaml

_config = None


def _default_conf():
    import os
    return os.path.join(os.path.dirname(__file__), 'plotting_config.yaml')


def _default_color_conf():
    import os
    return os.path.join(os.path.dirname(__file__), 'color.yaml')


class PlotingConfig:
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


class ColorConfig:
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = _default_color_conf()
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
