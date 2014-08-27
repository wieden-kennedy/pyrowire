import unittest

from pyrowire import pyrowire as pyro
from pyrowire.config import configurator as config
from redis import Redis
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
        _expected_response = config.validators(self.topic)['profanity']
        _message = 'fuck'
        _response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890' % (self.topic, _message), follow_redirects=True)

        _data = str(_response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(_response.status, "200 OK")
        self.assertEqual(_data, _expected_response)

    def test_message_too_long(self):
        _expected_response = config.validators(self.topic)['length']
        _message = 'bkndlznbezfmuktjdsvosezchjlgvjznblxvoihpdasfxifpiupzlzrphfswozdjbgiohemtbyuuoqzvbxiixhkyryheizoqxnp' \
                'tutihnohujythamvptubsrdjlgxqfmltvdfvksbmpddsdfasdfasdfasdweljweoibtgsgdlicwwnmgeduvrezso'
        _response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890' % (self.topic, _message), follow_redirects=True)

        _data = str(_response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(_response.status, "200 OK")
        self.assertEqual(_data, _expected_response)

    def test_message_zero_length(self):
        _expected_response = config.validators(self.topic)['length']
        _message = ''
        _response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890' % (self.topic, _message), follow_redirects=True)

        _data = str(_response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(_response.status, "200 OK")
        self.assertEqual(_data, _expected_response)

    def test_message_not_parseable(self):
        _expected_response = config.validators(self.topic)['parseable']
        _message = '%F0%9F%98%AC'
        _response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890' % (self.topic, _message), follow_redirects=True)

        _data = str(_response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(_response.status, "200 OK")
        self.assertEqual(_data, _expected_response)

    def test_good_message(self):
        _messages = ['Frank', 'Joe Bob', 'Mary Kate ']
        _expected_response = config.accept_response(self.topic)
        for n in _messages:
            _response = self.test_app.get('/queue/%s?Body=%s&From=+1234567890' % (self.topic, n), follow_redirects=True)

            _data = str(_response.data).split('<Body>')[1].split('</Body>')[0]

            self.assertEqual(_response.status, "200 OK")
            self.assertEqual(_data, _expected_response)

if __name__ == '__main__':
    unittest.main()
