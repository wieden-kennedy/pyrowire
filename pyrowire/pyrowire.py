from flask import Flask

import config.configuration as config
import runner.runner as runner
from validators.validators import profanity, parseable, length
from routes.queue_message import queue_message

FLASK = Flask(__name__, static_url_path='/static')
FLASK.register_blueprint(queue_message, url_prefix='/queue')

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

if __name__ == '__main__':
    import resources.settings
    configure(settings=resources.settings)
    runner.run()
