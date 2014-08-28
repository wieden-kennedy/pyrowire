import random
import string
import unittest

from redis import Redis

from pyrowire import pyrowire as pyro
from pyrowire.config import configuration as config
from test import test_settings


pyro.configure(settings=test_settings)

class TestMessageQueue(unittest.TestCase):
    def setUp(self):
        self.test_app = config.app().test_client()
        self.topic = 'sample'

        self.redis = Redis(config.redis('host'), config.redis('port'), config.redis('db'), config.redis('password'))

    def tearDown(self):
        self.redis.delete('%s.submitted' % self.topic)
        self.redis.delete('%s.pending' % self.topic)
        self.redis.delete('%s.completed' % self.topic)

    def test_profane_message(self):
        expected_response = config.validators(self.topic)['profanity']
        sid = ''.join(random.choice(string.ascii_letters) for i in range(34))
        message = 'fuck'
        response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890&MessageSid=%s' % (self.topic, message, sid),
                                     follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)

    def test_message_too_long(self):
        message = ''.join(random.choice(string.ascii_letters) for i in range(161))
        sid = ''.join(random.choice(string.ascii_letters) for i in range(34))
        expected_response = config.validators(self.topic)['length']
        response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890&MessageSid=%s' % (self.topic, message, sid),
                                     follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)
        
    def test_message_exceeds_twilio_maximum_length(self):
        message = ''.join(random.choice(string.ascii_letters) for i in range(1600))
        sid = ''.join(random.choice(string.ascii_letters) for i in range(34))
        expected_response = config.validators(self.topic)['length']
        response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890&MessageSid=%s' % (self.topic, message, sid),
                                     follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)

    def test_message_zero_length(self):
        expected_response = config.validators(self.topic)['length']
        message = ''
        sid = ''.join(random.choice(string.ascii_letters) for i in range(34))
        response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890&MessageSid=%s' % (self.topic, message, sid),
                                     follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)

    def test_message_not_parseable(self):
        expected_response = config.validators(self.topic)['parseable']
        message = '%F0%9F%98%AC'
        sid = ''.join(random.choice(string.ascii_letters) for i in range(34))
        response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890&MessageSid=%s' % (self.topic, message, sid),
                                     follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)

    def test_good_message(self):
        messages = ['Frank', 'Joe Bob', 'Mary Kate ']
        sid = ''.join(random.choice(string.ascii_letters) for i in range(34))
        expected_response = config.accept_response(self.topic)
        for n in messages:
            response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890&MessageSid=%s' % (self.topic, n, sid),
                                         follow_redirects=True)

            data = str(response.data).split('<Body>')[1].split('</Body>')[0]

            self.assertEqual(response.status, "200 OK")
            self.assertEqual(data, expected_response)

if __name__ == '__main__':
    unittest.main()
