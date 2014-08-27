import pyrowire.config as config

# function decorators
# ----------------------------------------------------------------------------------------------------------------------
def handler(topic=None):
    """
    decorator function that adds a processor to its topic in the application config
    :param topic: name of the topic to which to add the function
    :return: function, add_processor
    """
    def add_processor(f):
        config.add_handler(topic, f)

    return add_processor

def validator(name=None):
    """
    decorator function that adds a filter to the application's filter set
    :param name: name of the filter (should match the function name)
    :return: function, add_filter
    """
    def add_filter(f):
        filter_name = name or f.__name__
        config.add_validator(f)

    return add_filter
