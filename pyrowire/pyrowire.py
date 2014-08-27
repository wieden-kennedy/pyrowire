from datetime import datetime
import json
from multiprocessing import Process
import time

from flask import Flask, request
from redis import Redis
from redis.exceptions import ConnectionError, TimeoutError
import twilio.twiml as twiml

import config.configuration as config
from messaging.sms import sms
from messaging.message import message_from_request
import runner.runner as runner
from validators.validators import profanity, parseable, length

FLASK = Flask(__name__, static_url_path='/static')

# configure - the setup method
# ----------------------------------------------------------------------------------------------------------------------
def configure(settings=None):
    """
    wires up pyrowire application dict, as well as logger, and makes them available to the global scope,
    so the underlying flask application can have access to it when a message hits the main route
    :param settings: the settings.py file that configures the application
    :raises TypeError if settings is NoneType
    """
    if not settings:
        raise TypeError('Settings cannot be null.')

    config.configure(settings, flask=FLASK)
    config.add_validator(profanity)
    config.add_validator(parseable)
    config.add_validator(length)

    FLASK.logger.setLevel(config.log_level())

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
        if type(e) in [KeyError, TypeError]:
            try:
                timestamp = time.time()
                date_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                error = {'message': message, 'error': str(e)}
                redis.hset('%s.error' % topic, date_timestamp, error)
            except:
                pass
        # log the error and return the topic's error response
        FLASK.logger.log(e)
        response.message(config.error_response(topic))
        return str(response)

if __name__ == '__main__':
    import resources.settings
    configure(settings=resources.settings)
    runner.run()
