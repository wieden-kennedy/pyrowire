import unittest

from pyrowire import pyrowire as pyro
from pyrowire.messaging.send import sms
from test import test_settings

pyro.configure(settings=test_settings)


class TestTwilioClient(unittest.TestCase):
    def test_twilio(self):
        job_data = {'message': 'Test', 'final_message': 'TestTestTest', 'number': '+15039280913', 'topic':'sample'}
        success = sms(message_data=job_data, key='final_message')
        self.assertTrue(success)

    def test_no_message(self):
        success = sms(message_data=None, key='final_message')
        self.assertFalse(success)

    def test_custom_key(self):
        job_data = {'message':'Test', 'final_message': 'TestTestTest', 'number': '+15039280913', 'topic':'sample'}
        success = sms(message_data=job_data, key='final_message')
        self.assertTrue(success)

    def test_no_reply_or_key(self):
        job_data = {'message':'Test', 'final_message': 'TestTestTest', 'number': '+15039280913', 'topic':'sample'}
        success = sms(message_data=job_data)
        self.assertFalse(success)



