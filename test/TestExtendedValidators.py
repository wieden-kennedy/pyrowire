import unittest

from redis import Redis

from pyrowire import pyrowire as pyro
from pyrowire.decorators.decorators import *
from test import test_settings

app = pyro.configure(settings=test_settings)

@validator(name='must_say_yo')
def must_say_yo(message_data=None):
    import re
    return not re.search(r'(yo)', message_data['message'].lower())


class TestExtendedValidators(unittest.TestCase):

    def setUp(self):
        self.test_app = config.app().test_client()
        self.topic = 'sample'

        self.redis = Redis(config.redis('host'),
                           config.redis('port'),
                           config.redis('db'),
                           config.redis('password'))

    def tearDown(self):
        self.redis.delete('%s.submitted' % self.topic)
        self.redis.delete('%s.pending' % self.topic)
        self.redis.delete('%s.completed' % self.topic)

    def test_no_yo(self):
        _expected_response = config.validators(self.topic)['must_say_yo']
        _message = 'Keith Hamilton'
        _response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890' % (self.topic, _message), follow_redirects=True)

        _data = str(_response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(_response.status, "200 OK")
        self.assertEqual(_data, _expected_response)

    def test_yo_present(self):
        _expected_response = config.accept_response(self.topic)
        _message = 'yo, Keith!'
        _response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890' % (self.topic, _message), follow_redirects=True)

        _data = str(_response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(_response.status, "200 OK")
        self.assertEqual(_data, _expected_response)

if __name__ == '__main__':
    unittest.main()
