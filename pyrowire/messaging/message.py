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
    if req.method == 'GET':
        message = {'message': req.args['Body'], 'number': req.args['From'], 'topic': topic}
    # if request method is 'POST', use request form
    else:
        message = {'message': req.form['Body'], 'number': req.form['From'], 'topic': topic}
    return message