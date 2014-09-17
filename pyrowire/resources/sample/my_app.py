import pyrowire
import my_settings

# configure the pyrowire application
pyrowire.configure(my_settings)

# all app.processor methods need to be annotated with the topic for which they process
# and take one kwarg, 'message_data'
@pyrowire.handler(topic='my_topic')
def my_processor(message_data):
    if not message_data:
        raise TypeError("message_data must not be None")
    # insert handler logic here
    return message_data

# all pyro.filter methods need to be annotated with the name of the filter
# and take one kwarg, 'message_data'
@pyrowire.validator(name='my_validator')
def my_filter(message_data):
    if not message_data:
        raise TypeError("message_data must not be None")
    # insert validation logic here
    # validators should try to prove that the message is invalid, i.e., return True
    return True

if __name__ == '__main__':
    pyrowire.run()
