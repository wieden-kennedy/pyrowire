from datetime import datetime
import json
import logging
import time

from redis import Redis
from redis.exceptions import ConnectionError, TimeoutError

import pyrowire.config.configuration as config
from pyrowire.resources.settings import *

def process_queue_item(topic=None, persist=True):
    """
    method that block pops items from a redis queue and processes them according to the defined processor for the topic.
    default behavior is persistent, i.e., will run as long as the worker is alive.
    :param topic: string, the topic for which to process queue items
    :param persist: boolean, default=True, whether to keep the process alive indefinitely
    :return: implicit None if persistent, explicit None if not persistent
    """

    log_level = config.log_level() or logging.DEBUG
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)

    redis = Redis(config.redis('host'), config.redis('port'), config.redis('db'), config.redis('password'))
    job_data = None
    job_sid = None

    while True:
        try:
            queue, job_data = redis.blpop('%s.%s' % (topic, 'submitted'))
            # if job_data was found, i.e., there was an item in queue, proceed. If not, wait for the next one
            if job_data:
                job_data = json.loads(job_data)
                job_sid = job_data['sid']
                # insert the record for this job into the pending queue for this topic
                redis.hset('%s.%s' % (topic, 'pending'), job_sid, json.dumps(job_data))
                # attempt to process the message
                config.handler(topic)(message_data=job_data)
                # add job to complete queue and remove from pending queue
                redis.hdel('%s.%s' % (topic, 'pending'),
                           job_sid)
                redis.hset('%s.%s' % (topic, 'complete'),
                           job_sid, json.dumps(job_data))
        except (ConnectionError, TimeoutError, IndexError, TypeError, KeyError), e:
            # if the error was not a redis connection or timeout error, log the error to redis
            # if the log to redis fails, let it go
            if type(e) in [KeyError, TypeError]:
                try:
                    timestamp = time.time()
                    date_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    error = {'message': job_data, 'error': str(e)}
                    redis.hset('%s.error' % topic, date_timestamp, error)
                except (ConnectionError, TimeoutError):
                    pass
            logger.error(e)

        if not persist:
            return job_sid
