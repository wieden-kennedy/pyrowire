import random
import string
import unittest

from redis import Redis

from pyrowire import pyrowire as pyro
from pyrowire.config import configuration as config
from pyrowire.messaging.message import message_from_request
from test import test_settings

pyro.configure(settings=test_settings)

class TestMessageQueue(unittest.TestCase):
    def setUp(self):
        self.test_app = config.app().test_client()
        self.topic = 'sample'
        self.inbound = '/queue/%s?Body=%s&From=+1234567890&MessageSid=%s&NumMedia=%s'
        self.sid = ''.join(random.choice(string.ascii_letters) for i in range(34))

        self.redis = Redis(config.redis('host'), config.redis('port'), config.redis('db'), config.redis('password'))

    def tearDown(self):
        self.redis.delete('%s.submitted' % self.topic)
        self.redis.delete('%s.pending' % self.topic)
        self.redis.delete('%s.completed' % self.topic)

    def test_profane_message(self):
        expected_response = config.validators(self.topic)['profanity']
        message = 'fuck'
        response = self.test_app.get(self.inbound % (self.topic, message, self.sid, 0), follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)

    def test_message_too_long(self):
        message = ''.join('c' for i in range(161))
        expected_response = config.validators(self.topic)['length']
        response = self.test_app.get(self.inbound % (self.topic, message, self.sid, 0), follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)
        
    def test_message_exceeds_twilio_maximum_length(self):
        message = ''.join('c' for i in range(1600))
        expected_response = config.validators(self.topic)['length']
        response = self.test_app.get(self.inbound % (self.topic, message, self.sid, 0), follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)

    def test_message_zero_length(self):
        expected_response = config.validators(self.topic)['length']
        message = ''
        response = self.test_app.get(self.inbound % (self.topic, message, self.sid, 0), follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)

    def test_message_not_parseable(self):
        expected_response = config.validators(self.topic)['parseable']
        message = '%F0%9F%98%AC'
        response = self.test_app.get(self.inbound % (self.topic, message, self.sid, 0), follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)

    def test_good_message(self):
        messages = ['Frank', 'Joe Bob', 'Mary Kate ']
        expected_response = config.accept_response(self.topic)
        for n in messages:
            response = self.test_app.get(self.inbound % (self.topic, n, self.sid, 0), follow_redirects=True)

            data = str(response.data).split('<Body>')[1].split('</Body>')[0]

            self.assertEqual(response.status, "200 OK")
            self.assertEqual(data, expected_response)

    def test_additional_arguments(self):
        message = 'Hello there.'
        from_country = 'USA'
        from_state = 'OR'
        from_city = 'Portland'
        from_zip = '97209'

        expected_response = config.accept_response(self.topic)
        inbound_message = self.inbound + '&FromCountry=%s&FromState=%s&FromCity=%s&FromZip=%s'
        response = self.test_app.get(inbound_message %
                                     (self.topic, message, self.sid, 0, from_country, from_state, from_city, from_zip),
                                     follow_redirects=True)

        data = str(response.data).split('<Body>')[1].split('</Body>')[0]

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(data, expected_response)


    def test_message_construction(self):
        # no additional args
        class Request(object):
            def __init__(self):
                self.method = 'GET'
                self.args = {
                    'From': '+1234567890',
                    'Body': 'Hello, there.',
                    'MessageSid': ''.join(random.choice(string.ascii_letters) for i in range(34))
                }
                self.view_args = {
                    'topic': 'sample'
                }

        request = Request()
        message = message_from_request(request=request)
        self.assertTrue(message['number'], request.args['From'])
        self.assertTrue(message['message'], request.args['Body'])
        self.assertTrue(message['sid'], request.args['MessageSid'])

        # additional args
        request.args['FromCountry'] = 'USA'
        request.args['FromState'] = 'OR'
        request.args['FromCity'] = 'Portland'
        request.args['FromZip'] = '97209'

        additional_args_message = message_from_request(request=request)

        self.assertTrue(additional_args_message['from_country'], request.args['FromCountry'])
        self.assertTrue(additional_args_message['from_state'], request.args['FromState'])
        self.assertTrue(additional_args_message['from_city'], request.args['FromCity'])
        self.assertTrue(additional_args_message['from_zip'], request.args['FromZip'])

        # with media
        request.args['NumMedia'] = 2
        request.args['MediaUrl0'] = 'http://some.com/some.jpg',
        request.args['MediaContentType0'] = 'image/jpeg'
        request.args['MediaUrl1'] = 'http://some.com/some_other.jpg',
        request.args['MediaContentType1'] = 'image/jpeg'

        media_message = message_from_request(request=request)

        self.assertEqual(media_message['media']['count'], 2)
        for item in [request.args['MediaUrl0'], request.args['MediaUrl1']]:
            self.assertTrue(item in media_message['media']['media'].keys())
        for item in [request.args['MediaContentType0'], request.args['MediaContentType1']]:
            self.assertTrue(item in media_message['media']['media'].values())

if __name__ == '__main__':
    unittest.main()
