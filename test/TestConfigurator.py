import os
import unittest

from pyrowire import pyrowire as pyro
import pyrowire.config.configuration as config
from test import test_settings

class TestConfigurator(unittest.TestCase):

    def setUp(self):
        pyro.configure(settings=test_settings)

    def test_configuration(self):
        profile = test_settings.PROFILES[os.environ['ENV'].lower()]
        topics = test_settings.TOPICS

        # profile
        self.assertEqual(profile['debug'], config.debug())
        self.assertEqual(profile['host'], config.host())
        self.assertEqual(profile['log_level'], config.log_level())
        self.assertEqual(profile['port'], config.port())
        self.assertEqual(profile['redis'], config.redis())
        for key, value in [(k, v) for k, v in profile['redis'].items()]:
            self.assertEqual(value, config.redis(key))

        # topics
        self.assertEqual(topics, config.topics())
        for key, value in [(k, v) for k, v in topics.items()]:
            self.assertEqual(value, config.topics(key))

        # properties
        for t in [k for k in test_settings.TOPICS.keys()]:
            self.assertEqual(test_settings.TOPICS[t]['properties'], config.properties(t))
            for p in [j for j in config.properties(t).keys()]:
                self.assertEqual(test_settings.TOPICS[t]['properties'][p], config.properties(t,p))

