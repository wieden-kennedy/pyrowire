import itertools

from pyrowire.resources import profanity as profanity_terms
import pyrowire.config as config

# default validators
# ----------------------------------------------------------------------------------------------------------------------
def profanity(message_data=None):
    """
    message filter that ensures none of the terms found in the profanity set are found in the message
    being sent to the application. Uses itertools to take while terms do not match the message. As soon as a match
    is found the loop breaks. If no matches are found (message is not profane) length of _not_in list will equal
    the length of the profanity terms list.
    :param message_data: the message data that should be checked for profanity
    :return: boolean, whether the list of iterated profane terms matches the list of the terms not found in message
    :raise e: Connection or timeout error with redis
    """
    profane_terms = profanity_terms.profanity
    not_in = []
    message = message_data['message'].replace(' ', '').lower()
    for i in itertools.takewhile(lambda x: x not in message, profane_terms):
        not_in.append(i)

    # if the lengths of the two lists match, the term is not profane
    return len(not_in) != len(profane_terms)

def length(message_data=None):
    """
    message filter that asserts the sent message is both of length greater than 0 and less than or equal to
    the maximum allowable length for a message, per the configuration settings
    :param message_data: the message_data object to be validated
    :return: boolean, whether the message is within the tolerated length
    """
    max_length = config.max_message_length(message_data['topic'])
    return len(message_data['message']) == 0 or max_length < len(message_data['message'])

def parseable(message_data=None):
    """
    message filter that asserts the sent message is parseable. The allowed range of characters includes alphanumeric
    and punctuation that is reasonable to expect in a text message (e.g., '|' and '\' are not included)
    :param message_data: the message data to be validated
    :return: boolean, whether the message is parseable by the confines of acceptable characters
    """
    acceptable = range(97, 123) + range(65, 91) + range(48, 58) + range(33, 43) + range(44, 48) + [58, 63, 64, 94]
    return any(ord(c) not in acceptable for c in message_data['message'].replace(' ', ''))
