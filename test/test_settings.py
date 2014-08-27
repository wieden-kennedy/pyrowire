import logging

TOPICS = {
    'sample': {
        'send_on_accept': False,
        'accept_response': 'Excellent, this is.',
        'error_response': 'An error in the request, there was, hmmmm?',
        'validators': {
            'profanity': 'You kiss your mother with that mouth?',
            'length': 'Messages need to be fewer than 160 characters, and more than zero.',
            'parseable': 'We can only accept alphanumeric and punctuation characters.',
            'must_say_yo': 'You gotta say \'yo\', yo.'
        },
        'properties': {},
        'twilio': {
            # twilio test credentials -- not live
            'account_sid': '',
            'auth_token': '',
            'from_number': '+1234567890'
        },
        'max_message_length': 160
    }
}

PROFILES = {
    'dev': {
        'debug': True,
        'log_level': logging.DEBUG,
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': ''
        },
        'host': 'localhost',
        'port': 5000
    }
}
