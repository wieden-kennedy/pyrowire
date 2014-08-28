from flask import Flask

import config.configuration as config
import runner.runner as runner
from validators.validators import profanity, parseable, length
from routes.queue_message import queue_message

FLASK = Flask(__name__, static_url_path='/static')
FLASK.register_blueprint(queue_message, url_prefix='/queue')

def configure(settings=None):
    """
    wires up configuration for pyrowire app, sets Flask logging level to level from config settings
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
