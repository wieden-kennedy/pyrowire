from flask import Blueprint, request, current_app
from redis import Redis
from redis.exceptions import ConnectionError, TimeoutError

import pyrowire.config.configuration as config

reports = Blueprint('message_queue', __name__)

@reports.route('/<topic>', methods=['GET', 'POST'])
def report(topic):
    redis = Redis(config.redis('host'), config.redis('port'), config.redis('db'), config.redis('password'))
    complete = redis.hgetall('%s.complete' % topic)
    pending = redis.hgetall('%s.pending' % topic)
    errors = redis.hgetall('%s.error' % topic)

