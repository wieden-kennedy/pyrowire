import logging

from twilio.rest import TwilioRestClient

import pyrowire.config.configuration as config


# Twilio methods - SMS
# ----------------------------------------------------------------------------------------------------------------------
def sms(data=None, key='reply'):
    """
    wrapper function around the twilio.rest api to send a message
    :param data: the message data object containing the handled message information
    :param key: the key for the message data object that holds the final response
    :return: boolean, whether the twilio message was created successfully.
    """
    logging.basicConfig(level=config.log_level())
    logger = logging.getLogger(__name__)

    if not data:
        logger.error(TypeError('Message data must be provided'))
        return False

    twilio_config = config.twilio(data['topic'])
    twilio_client = TwilioRestClient(twilio_config['account_sid'], twilio_config['auth_token'])
    try:
        twilio_client.messages.create(to=data['number'], from_=twilio_config['from_number'], body=data[key])
        return True
    except Exception, e:
        logger.error(e)
        return False

def mms(data=None, key='reply', media_url=None):
    """
    wrapper function around the twilio.rest api to send a message
    ** Currently only works with Short Codes in the US **
    :param data: the message data object containing the handled message information
    :param key: the key for the message data object that holds the final response
    :return: boolean, whether the twilio message was created successfully.
    """
    logging.basicConfig(level=config.log_level())
    logger = logging.getLogger(__name__)

    if not data or not media_url:
        missing_item = 'data' if not data else 'media_url'
        logger.error(TypeError('Message %s must be provided' % missing_item))
        return False

    twilio_config = config.twilio(data['topic'])
    twilio_client = TwilioRestClient(twilio_config['account_sid'], twilio_config['auth_token'])
    try:
        twilio_client.messages.create(to=data['number'],
                                      from_=twilio_config['from_number'],
                                      body=data[key],
                                      media_url=media_url)
        return True
    except Exception, e:
        logger.error(e)
        return False
