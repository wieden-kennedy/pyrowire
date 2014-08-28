import unittest

from pyrowire import pyrowire as pyro
from pyrowire.messaging.sms import sms
from test import test_settings

pyro.configure(settings=test_settings)


class TestTwilioClient(unittest.TestCase):
    def test_twilio(self):
        job_data = {'message': 'Test', 'final_message': 'TestTestTest', 'number': '+15039280913', 'topic':'sample'}
        success = sms(data=job_data, key='final_message')
        self.assertTrue(success)

    def test_no_message(self):
        success = sms(data=None, key='final_message')
        self.assertFalse(success)

    def test_no_key(self):
        job_data = {'message':'Test', 'final_message': 'TestTestTest', 'number': '+15039280913', 'topic':'sample'}
        success = sms(data=job_data, key=None)
        self.assertFalse(success)



