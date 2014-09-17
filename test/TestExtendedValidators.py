import random
import string
import unittest

from redis import Redis

from pyrowire import pyrowire as pyro
from pyrowire.decorators.decorators import *
from test import test_settings

app = pyro.configure(test_settings)

@validator(name='must_say_yo')
def must_say_yo(message_data):
    import re
    return not re.search(r'(yo)', message_data['message'].lower())


class TestExtendedValidators(unittest.TestCase):

    def setUp(self):
        self.test_app = config.app().test_client()
        self.topic = 'sample'
        self.number= '+1234567890'
        self.sid = ''.join(random.choice(string.ascii_letters) for i in range(34))
        self.inbound = '/queue/%s?Body=%s&From=%s&MessageSid=%s'
        self.redis = Redis(config.redis('host'),
                           config.redis('port'),
                           config.redis('db'),
                           config.redis('password'))

    def tearDown(self):
        self.redis.delete('%s.submitted' % self.topic)
        self.redis.delete('%s.pending' % self.topic)
        self.redis.delete('%s.completed' % self.topic)

    def test_no_yo(self):
        expected_response = config.validators(self.topic)['must_say_yo']
        message = 'Keith Hamilton'
        response = self.test_app.get(self.inbound % (self.topic, message, self.number, self.sid), follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)

    def test_yo_present(self):
        expected_response = config.accept_response(self.topic)
        message = 'yo, Keith!'
        response = self.test_app.get(self.inbound % (self.topic, message, self.number, self.sid), follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)

if __name__ == '__main__':
    unittest.main()
