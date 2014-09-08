from datetime import datetime
import json
import time

from flask import Blueprint, request, current_app
from redis import Redis
from redis.exceptions import ConnectionError, TimeoutError
import twilio.twiml as twiml

import pyrowire.config.configuration as config
from pyrowire.messaging.message import call_from_request

IN_PROGRESS_KEY = "in_progress"

voice_call = Blueprint('voice_call', __name__)
voice_queue = Blueprint('voice_queue', __name__)
redis = Redis(config.redis('host'), config.redis('port'), config.redis('db'), config.redis('password'))

@voice_call.route('/<call_topic>', methods=['GET', 'POST'])
def call(call_topic):
    call_data = call_from_request(request=request)
    response = None
    if not in_progress(call_topic):
        try:
            redis.hset('%s.%s' % (call_topic, 'pending'), call_data['sid'], json.dumps(call_data))
            response = config.handler(call_topic)(message_data=call_data)
            redis.hdel('%s.%s' % (call_topic, 'pending'), call_data['sid'], json.dumps(call_data))
            redis.hset('%s.%s' % (call_topic, 'complete'), call_data['sid'], json.dumps(call_data))
        except (ConnectionError, TimeoutError, IndexError, TypeError, KeyError), e:
            # if the error was not a redis connection or timeout error, log the error to redis
            # if the log to redis fails, let it go
            if type(e) in [KeyError, TypeError]:
                try:
                    timestamp = time.time()
                    date_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    error = {'message': call_data, 'error': str(e)}
                    redis.hset('%s.error' % call_topic, date_timestamp, error)
                except (ConnectionError, TimeoutError):
                    pass
            current_app.logger.log(e)
            response = twiml.Response()
            response.say(config.topics(call_topic)['call_error_response'])
    else:
        response = twiml.Response()
        response.say(config.topics(call_topic)['call_busy_response'])

    return str(response)

def in_progress(topic):
    return redis.exists('%s.%s' % (topic, IN_PROGRESS_KEY))

def lock_call(topic):
    redis.setex('%s.%s' % (topic, IN_PROGRESS_KEY), config.topics(topic)['call_timeout'], "true")

def unlock_call(topic):
    redis.delete('%s.%s' % (topic, IN_PROGRESS_KEY))
