# Utility methods
# ----------------------------------------------------------------------------------------------------------------------
def message_from_request(req=None, topic=None):
    # if request method is 'GET', use request arguments
    """
    Utility method to extract relevant sms message data from inbound message
    :param req: the flask request object
    :param topic: the topic for which the message has been sent
    :return: message, a dict object of the message data
    """
    # queue endpoint only accepts 'GET' and 'POST' so safe from not checking for other method types
    # if request method is 'GET', use request args else use req.form
    req_data = req.args if req.method == 'GET' else req.form
    message = {'message': req_data['Body'], 'number': req_data['From'], 'sid': req_data['MessageSid'], 'topic': topic}
    return message