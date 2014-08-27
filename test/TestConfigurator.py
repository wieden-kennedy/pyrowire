import os
import unittest

from pyrowire import pyrowire as pyro
from test import test_settings
import pyrowire.config.configurator as config

class TestConfigurator(unittest.TestCase):

    def setUp(self):
        pyro.configure(settings=test_settings)

    def test_configuration(self):
        self.assertEqual(test_settings.TOPICS, config.topics())
        self.assertEqual(test_settings.PROFILES[os.environ['ENV'].lower()], config.profile())

    # tests not otherwise covered by other test suites
    def test_topics(self):
        for t in [k for k in test_settings.TOPICS.keys()]:
            self.assertEqual(test_settings.TOPICS[t], config.topics(t))
        self.assertEqual(test_settings.TOPICS, config.topics())

    def test_properties(self):
        for t in [k for k in test_settings.TOPICS.keys()]:
            self.assertEqual(test_settings.TOPICS[t]['properties'], config.properties(t))
            for p in [j for j in config.properties(t).keys()]:
                self.assertEqual(test_settings.TOPICS[t]['properties'][p], config.properties(t,p))

    def test_host(self):
        self.assertEqual(test_settings.PROFILES[os.environ['ENV'].lower()]['host'], config.host())

    def test_port(self):
        self.assertEqual(test_settings.PROFILES[os.environ['ENV'].lower()]['port'], config.port())

    def test_redis(self):
        _redis = test_settings.PROFILES[os.environ['ENV'].lower()]['redis']
        self.assertEqual(_redis, config.redis())
        for key in [k for k in _redis.keys()]:
            self.assertEqual(_redis[key], config.redis(key))
