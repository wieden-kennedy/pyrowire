from datetime import datetime
import json
import logging
from multiprocessing import Process
import time

from flask import Flask, request
from redis import Redis
from redis.exceptions import ConnectionError, TimeoutError
import twilio.twiml as twiml

import config.configuration as config
from messaging.sms import sms
from messaging.message import message_from_request
import resources.settings as pyro_settings
import runner.runner as runner
from validators.validators import profanity, parseable, length


FLASK = Flask(__name__, static_url_path='/static')
LOGGER = None

# wire - the setup method
# ----------------------------------------------------------------------------------------------------------------------
def configure(settings=pyro_settings):
    """
    wires up pyrowire application dict, as well as logger, and makes them available to the global scope,
    so the underlying flask application can have access to it when a message hits the main route
    :param settings: the settings.py file that configures the application
    """
    config.configure(settings, flask=FLASK)
    config.add_validator(profanity)
    config.add_validator(parseable)
    config.add_validator(length)

    global LOGGER
    logging.basicConfig(level=config.log_level())
    LOGGER = logging.getLogger(__name__)

# Flask routes
# ----------------------------------------------------------------------------------------------------------------------
@FLASK.route('/queue/<topic>', methods=['GET', 'POST'])
def queue_message(topic):
    """
    takes inbound request from Twilio API and parses out:
      - From (mobile number of sender)
      - Body (message sent via SMS)
    ensures body passes through all defined filters for the topic
    if filters pass, mobile number and message are queued in Redis for processing by worker(s).
    response is sent back using twiml based on outcome
    :return: string form of twiml response
    """
    message = message_from_request(req=request, topic=topic)
    redis = Redis(config.redis('host'), config.redis('port'), config.redis('db'), config.redis('password'))
    response = twiml.Response()
    try:
        # validator block
        # --------------------------------------------------------------------------------------------------------------
        # for each validator that is to be applied to the topic
        for name, func in [k for k in config.validators().items() if k[0] in config.validators(topic).keys()]:
            # run the message against the validator
            message_invalid = func(message_data=message)
            # if it fails to pass validation, get the error message, and return it to the SMS sender
            if message_invalid:
                message['validator_error'] = config.validators(topic)[name]
                # kick off parallel thread to handle response without blocking
                Process(target=sms, kwargs={'data': message, 'key': 'validator_error'}).start()
                # set the twiml response to the validator error message
                response.message(config.validators(topic)[name])
                return str(response)

        # if the message passed all filter validations, queue message in redis, and set the reply to successful
        redis.rpush('%s.%s' % (topic, 'submitted'), json.dumps(message))
        message['response'] = config.accept_response(topic)

        # if the twilio application is set to respond on successful receipt of message, send the accept message back.
        if config.send_on_accept(topic):
            # kick off parallel thread to handle response without blocking
            Process(target=sms, kwargs={'data': message, 'key': 'response'}).start()

        response.message(config.accept_response(topic))
        return str(response)

    except (ConnectionError, TimeoutError, KeyError, TypeError) as e:
        # if the error was not a redis connection or timeout error, log the error to redis
        # if the log to redis fails, let it go
        if type(e).__name__ in ['KeyError', 'TypeError']:
            try:
                _timestamp = time.time()
                _date_timestamp = datetime.fromtimestamp(_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                _error = {'message': message, 'error': str(e)}
                redis.hset('%s.error' % topic, _date_timestamp, _error)
            except:
                pass
        # log the error and return the topic's error response
        LOGGER.error(e)
        response.message(config.error_response(topic))
        return str(response)


if __name__ == '__main__':
    configure(settings=pyro_settings)
    runner.run()
