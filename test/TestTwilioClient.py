import unittest

from pyrowire import pyrowire as pyro
from pyrowire.messaging.send import sms
from test import test_settings

pyro.configure(test_settings)


class TestTwilioClient(unittest.TestCase):
    def test_twilio(self):
        job_data = {'message': 'Test', 'reply': 'TestTestTest', 'number': '+15039280913', 'topic':'sample'}
        success = sms(job_data)
        self.assertTrue(success)

    def test_no_message(self):
        self.assertRaises(TypeError, sms, None)

    def test_custom_key(self):
        job_data = {'message': 'Test', 'final_message': 'TestTestTest', 'number': '+15039280913', 'topic': 'sample'}
        success = sms(job_data, key='final_message')
        self.assertTrue(success)

    def test_no_reply_or_key(self):
        job_data = {'message': 'Test', 'final_message': 'TestTestTest', 'number': '+15039280913', 'topic': 'sample'}
        success = sms(job_data)
        self.assertFalse(success)



