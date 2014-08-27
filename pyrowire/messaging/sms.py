import logging

from twilio.rest import TwilioRestClient

import pyrowire.config.configurator as config


# Twilio methods - SMS
# ----------------------------------------------------------------------------------------------------------------------
def sms(data=None, key=None):
    """
    wrapper function around the twilio.rest api to send a message
    :param data: the message data object containing the handled message information
    :param key: the key for the message data object that holds the final response
    :return: boolean, whether the twilio message was created successfully.
    """
    logging.basicConfig(level=config.log_level())
    logger = logging.getLogger(__name__)

    if not data:
        logger.error(TypeError("Message data must be provided"))
        return False
    if not key:
        logger.error(TypeError("The key to the reply message must be provided"))
        return False

    twilio_config = config.twilio(data['topic'])
    twilio_client = TwilioRestClient(twilio_config['account_sid'], twilio_config['auth_token'])
    try:
        twilio_client.messages.create(to=data['number'], from_=twilio_config['from_number'], body=data[key])
        return True
    except Exception, e:
        logger.error(e)
        return False
