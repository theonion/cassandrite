import codecs
from collections import OrderedDict
from ConfigParser import ConfigParser
import os
import re


class Configuration(object):

    def __init__(self, rule_name, path, retention_rules, aggregation_method):
        self.rule_name = rule_name
        self.path = path
        self.regex = re.compile(self.path)
        self.retention_rules = [rule.strip() for rule in retention_rules.split(',')]
        self.aggregation_method = aggregation_method

    def __str__(self):
        data = {'rule_name': self.rule_name, 'path': self.path, 'regex': self.regex,
                'retention_rules': self.retention_rules, 'aggregation_method': self.aggregation_method}
        return str(data)


class ConfigurationStore(object):

    def __init__(self, filepath):
        self.configurations = OrderedDict()
        with codecs.open(filepath, 'r', encoding='utf8') as fh:
            parser = ConfigParser()
            parser.readfp(fh)
            for section in parser.sections():
                data = {'rule_name': section}
                for option in parser.options(section):
                    data[option] = parser.get(section, option)
                config = Configuration(**data)
                self.configurations[config.path] = config

    def get(self, name):
        for config in self.configurations.values():
            if re.match(config.regex, name):
                return config
        return None


filepath = os.path.join(os.path.dirname(__file__), 'default.ini')
config_store = ConfigurationStore(filepath)
