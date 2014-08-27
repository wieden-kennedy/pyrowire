import unittest

from pyrowire import pyrowire as pyro
from test import test_settings

pyro.configure(settings=test_settings)


class TestTwilioClient(unittest.TestCase):
    def test_twilio(self):
        _job_data = {'message': 'Test', 'final_message': 'TestTestTest', 'number': '+15039280913', 'topic':'sample'}
        success = pyro.sms(data=_job_data, key='final_message')
        self.assertTrue(success)

    def test_no_message(self):
        success = pyro.sms(data=None, key='final_message')
        self.assertFalse(success)

    def test_no_key(self):
        _job_data = {'message':'Test', 'final_message': 'TestTestTest', 'number': '+15039280913', 'topic':'sample'}
        success = pyro.sms(data=_job_data, key=None)
        self.assertFalse(success)



