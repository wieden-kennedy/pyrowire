import os

PYROWIRE = None

def configure(settings, flask):
    """
    sets up the global PYROWIRE object, containing all of the settings needed to run pyrowire.
    :param settings: the settings module that should be used to parse the settings
    :param flask: the underlying flask application that will be attached to pyrowire
    """
    global PYROWIRE
    PYROWIRE = {
        'env': os.environ['ENV'],
        'profile': settings.PROFILES[os.environ['ENV'].lower()],
        'topics': settings.TOPICS,
        'app': flask,
        'validators': {}
    }
# Utility - Application getters
#-----------------------------------------------------------------------------------------------------------------------
def topics(topic=None):
    if topic:
        return PYROWIRE['topics'][topic]
    return PYROWIRE['topics']

def validators(topic=None):
    if topic:
        return PYROWIRE['topics'][topic]['validators']
    return PYROWIRE['validators']

def properties(topic=None, key=None):
    if key:
        return PYROWIRE['topics'][topic]['properties'][key]
    return PYROWIRE['topics'][topic]['properties']

def twilio(topic=None):
    return PYROWIRE['topics'][topic]['twilio']

def handler(topic=None):
    if 'handler' in PYROWIRE['topics'][topic].keys():
        return PYROWIRE['topics'][topic]['handler']

def max_message_length(topic=None):
    return PYROWIRE['topics'][topic]['max_message_length']

def send_on_accept(topic=None):
    return PYROWIRE['topics'][topic]

def accept_response(topic=None):
    return PYROWIRE['topics'][topic]['accept_response']

def error_response(topic=None):
    return PYROWIRE['topics'][topic]['error_response']

# Utility - app setter
# ----------------------------------------------------------------------------------------------------------------------
def add_validator(validator=None):
    PYROWIRE['validators'][validator.__name__] = validator

def add_handler(topic=None, handler=None):
    PYROWIRE['topics'][topic]['handler'] = handler

# Utility - Profile getters
# ----------------------------------------------------------------------------------------------------------------------
def profile():
    return PYROWIRE['profile']

def host():
    return PYROWIRE['profile']['host']

def log_level():
    return PYROWIRE['profile']['log_level']

def port():
    return PYROWIRE['profile']['port']

def redis(key=None):
    if key:
        return PYROWIRE['profile']['redis'][key]
    return PYROWIRE['profile']['redis']

# Utility - global getter
# ----------------------------------------------------------------------------------------------------------------------
def app():
    return PYROWIRE['app']

