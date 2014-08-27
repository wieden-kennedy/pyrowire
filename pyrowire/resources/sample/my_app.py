import pyrowire

# instantiate the PyroApp object. No parameters required.
from pyrowire.resources.sample import my_settings

pyrowire.configure(settings=my_settings)

# all app.processor methods need to be annotated with the topic for which they process
# and take one kwarg, 'message_data'
@pyrowire.handler(topic='my_topic')
def my_processor(message_data=None):
    pass

# all pyro.filter methods need to be annotated with the name of the filter
# and take one kwarg, 'message_data'
@pyrowire.validator(name='my_validator')
def my_filter(message_data=None):
    pass

if __name__ == '__main__':
    pyrowire.run()
