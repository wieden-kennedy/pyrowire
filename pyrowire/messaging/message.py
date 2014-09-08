# Utility methods
# ----------------------------------------------------------------------------------------------------------------------
def message_from_request(request=None):
    # if request method is 'GET', use request arguments
    """
    Utility method to extract relevant sms message data from inbound message
    :param request: the flask request object
    :return: message, a dict object of the message data
    """
    # queue endpoint only accepts 'GET' and 'POST' so safe from not checking for other method types
    # if request method is 'GET', use request args else use request.form
    request_data = request.args if request.method == 'GET' else request.form
    message = {
        'message': request_data['Body'],
        'number': request_data['From'],
        'sid': request_data['MessageSid'],
        'topic': request.view_args['topic'],
        'from_city': get_if_available(request_data, 'FromCity'),
        'from_state': get_if_available(request_data, 'FromState'),
        'from_country': get_if_available(request_data, 'FromCountry'),
        'from_zip': get_if_available(request_data, 'FromZip'),
        'media': get_if_available(request_data, 'NumMedia'),
        'reply': None
    }
    return message

def call_from_request(request=None):
    # if request method is 'GET', use request arguments
    """
    Utility method to extract relevant call data from inbound message
    :param request: the flask request object
    :return: message, a dict object of the message data
    """
    # queue endpoint only accepts 'GET' and 'POST' so safe from not checking for other method types
    # if request method is 'GET', use request args else use request.form
    request_data = request.args if request.method == 'GET' else request.form
    message = {
        'number': request_data['From'],
        'sid': request_data['Sid'],
        'phone_number_sid': request_data['PhoneNumberSid'],
        'topic': request.view_args['topic'],
        'caller_name': get_if_available(request_data, 'CallerName'),
        'start_time': get_if_available(request_data, 'StartTime'),
        'direction': get_if_available(request_data, 'Direction')
    }
    return message

def get_if_available(request_data, key):
    """
    returns a value for the provided key if it exists in request data
    :param request_data: request data where key may exist
    :param key: key to look for
    :return: value from request data if key exists, or dict if key is 'NumMedia'
    """
    if key in request_data.keys():
        # special case, key == 'NumMedia'
        # if media was sent with the request, return a dict with the count of media items
        # as well as a key/value pair of media elements (as url/content_type)
        if key == 'NumMedia':
            media = {'count': int(request_data['NumMedia']), 'media': {}}
            for i in range(media['count']):
                media['media'][request_data['MediaUrl%s' % i]] = request_data['MediaContentType%s' % i]
            return media
        # if key is anything other than 'NumMedia', return its value
        return request_data[key]
    return None
