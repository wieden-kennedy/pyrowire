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
        'media': get_if_media(request_data),
        'reply': None
    }
    return message

def get_if_available(request_data, key):
    """
    returns a value for the provided key if it exists in request data
    :param request_data: request data where key may exist
    :param key: key to look for
    :return: value from request data if key exists
    """
    if key in request_data.keys():
        return request_data[key]
    return None

def get_if_media(request_data):
    """
    if media was sent along with the request, populate a dictionary object with the count
    and medial elements (as url/content_type k/v pairs)
    :param request_data: the request data to check for media
    :return: dictionary of media included with request
    """
    media = {
        'count': 0,
        'media': {}
    }
    if 'NumMedia' in request_data.keys() and int(request_data['NumMedia']) > 0:
        media['count'] = int(request_data['NumMedia'])
        for i in range(media['count']):
            media_url = request_data['MediaUrl%s' % i]
            media_type = request_data['MediaContentType%s' % i]
            media['media'][media_url] = media_type

    return media

