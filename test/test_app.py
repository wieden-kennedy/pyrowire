import pyrowire
import test_settings

pyrowire.configure(settings=test_settings)

@pyrowire.handler(topic='sample')
def mal_says(message_data=None):
    import random
    message = message_data['message'].split()
    random.shuffle(message)
    message_data['reply'] = 'Mal says: %s' % ' '.join(message)
    pyrowire.sms(data=message_data)

@pyrowire.validator(name='no_reavers')
def no_reavers(message_data=None):
    import re
    return re.search(r'\breaver\b', message_data['message'].lower())

if __name__ == '__main__':
    pyrowire.run()
