import ast
import json
import unittest
from multiprocessing import Process

from redis import Redis

from pyrowire import pyrowire
import pyrowire.config.configuration as config
from pyrowire.decorators.decorators import handler
import pyrowire.messaging.sms as sms
import pyrowire.runner.runner as runner
import pyrowire.tasks.tasks as tasks
from test import test_settings


pyrowire.configure(settings=test_settings)
topic = 'sample'

@handler(topic=topic)
def my_processor(message_data=None):
    message_data['final_data'] = message_data['message']
    Process(target=sms.sms, kwargs={'data': message_data, 'key': 'final_data'}).start()

class TestTasks(unittest.TestCase):

    def setUp(self):
        self.topic = topic

        self.redis = Redis(config.redis('host'),
                           config.redis('port'),
                           config.redis('db'),
                           config.redis('password'))

        self.redis.delete('%s.submitted' % self.topic)
        self.redis.delete('%s.pending' % self.topic)
        self.redis.delete('%s.completed' % self.topic)

    def tearDown(self):
        self.redis.delete('%s.submitted' % self.topic)
        self.redis.delete('%s.pending' % self.topic)
        self.redis.delete('%s.completed' % self.topic)

    def test_sample_task(self):
        # queue task
        message = {'message': 'You are strong in the ways of the Force.', 'number': '+1234567890', 'topic':'sample'}
        self.redis.rpush('%s.%s' % (self.topic, 'submitted'), json.dumps(message))
        # process task
        uuid = tasks.process_queue_item(self.topic, persist=False)
        # expect result in completed queue
        pending = self.redis.hget('%s.%s' % (self.topic, 'pending'), uuid)
        complete = ast.literal_eval(self.redis.hget('%s.%s' % (self.topic, 'complete'), uuid))

        self.assertIsNone(pending)
        self.assertIsNotNone(complete)
        self.assertEqual(complete['number'], '+1234567890')
        self.assertTrue('final_data' in complete)
        self.assertEqual(complete['final_data'], complete['message'])

    def test_pyro_work(self):
        # queue task
        message = {'message': 'You are strong in the ways of the Force.', 'number': '+1234567890', 'topic':'sample'}
        self.redis.rpush('%s.%s' % (self.topic, 'submitted'), json.dumps(message))
        # process task
        uuid = runner.work(topic=self.topic, persist=False)

        # expect result in completed queue
        pending = self.redis.hget('%s.%s' % (self.topic, 'pending'), uuid)
        complete = ast.literal_eval(self.redis.hget('%s.%s' % (self.topic, 'complete'), uuid))

        self.assertIsNone(pending)
        self.assertIsNotNone(complete)
        self.assertEqual(complete['number'], '+1234567890')
        self.assertTrue('final_data' in complete)
        self.assertEqual(complete['final_data'], complete['message'])


if __name__ == '__main__':
    unittest.main()
