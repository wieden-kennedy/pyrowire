Settings
========
Once you've got your validators and handlers set up, you'll need to dial in your config file. ``pyrowire`` uses a python file for settings configuration.
for its configuration files. To check out the sample settings file, look
`here <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/my_settings.py>`_. pyrowire's configuration files are broken down into two sections:

- **Topics** (Twilio application-specific settings). The Topics block can have as many topic dictionaries are are needed.
- **Profiles** (environment profile-specific settings). There is one block per run environment *(DEV/STAGING/PROD)*

Defining a Topic
----------------
To start out, here's what the topic section of a ``pyrowire`` settings file looks like:

.. code:: python

    TOPICS = {
        'my_topic': {
            # send_on_accept determines whether to send an additional accept/success
            # message upon successfully receiving an SMS.
            # NOTE: this will result in two return messages per inbound message
            'send_on_accept': False,
            # global accept (success) and error messages for your app
            'accept_response': 'Great, we\'ll get right back to you.',
            'error_response': 'It seems like an error has occurred...please try again.',
            # key/value pairs for application-specific validators and their responses
            # if a message fails to pass validation.
            # Define your custom validators here, or change the message
            # for an existing validator.
            'validators': {
                'profanity': 'You kiss your mother with that mouth? No profanity, please.',
                'length': 'Your message exceeded the maximum allowable character limit' + \
                            '(or was empty). Please try again .',
                'parseable': 'Please only use alphanumeric and punctuation characters.'
            },
            # properties are any non-pyrowire-specific properties that you will need to
            # run your handler, such as an API key to some external service.
            'properties': {},
            # Twilio account credentials section, where the account credentials for your
            # application-specific account are stored
            'twilio': {
                'account_sid': '',
                'auth_token': '',
                'from_number': '+1234567890'
            },
            # the default max length for a single message segment, per twilio, is 160 chars
            # but you can set this anything under 1600.
            'max_message_length': 160
        }
    }

Let's break that down a bit.

.. code:: python

    TOPICS = {
        'my_topic': {

This is the beginning of the applications dict, and, we have defined one topic, ``my_topic``. Next, we have:

.. code:: python

    # send_on_accept determines whether to send an additional accept/success message upon
    # successfully receiving an SMS.
    # NOTE: this will result in two return messages per inbound message
    'send_on_accept': False,
    # global accept (success) and error messages for your app
    'accept_response': 'Great, we\'ll get right back to you.',
    'error_response': 'It seems like an error has occurred...please try again later.',

-  **send\_on\_accept** enables or disables your app from actually sending a reply message immediately after the incoming
SMS was successfully accepted. Setting this to ``False`` will prevent your app from sending two return messages for every one it receives.
-  **accept\_response** and **error\_response** are respectively the messages that will be returned in the event of a
success or error. *Note:* error\_response will always send if an error occurs.

Next we have **validators**:

.. code:: python

    # key/value pairs for application-specific validators and their responses if a
    # message fails to pass validation.
    # Define your custom validators here. If you wish to change the response message
    # of a default validator, you can do that here.
    'validators': {
        'profanity': 'You kiss your mother with that mouth? No profanity, please.',
        'length': 'Your message exceeded the maximum allowable character limit' + \
                            '(or was empty). Please try again .',
        'parseable': 'Please only use alphanumeric and punctuation characters.'
    },

**profanity**, **length**, and **parseable** are the default validators for your app. To omit any one of these, comment out or
remove the item from the application's validators definition. Changing the message will change the return message sent to
the user if his/her message fails to pass the validator.

It is in this block that you would add any custom validators and their respective fail messages if you add validators to your
application. Remember, excluding a validator from an app config will cause it to not be used on any incoming messages for
that application; this means you can selectively apply different validators to different applications.

Next are properties:

.. code:: python

            # properties are any non-pyrowire-specific properties that you will need to
            # run your handler, such as an API key to some external service.
            'properties': {},

Properties are used for very specific application purposes. Say you want to translate all incoming messages into
Yoda-speak, and you need to hit an API for that...this is where you can add in your API key. The properties property in
the app config is just a catch-all spot for your application-specific custom properties.

In your handler method, then, you could access this as follows:

.. code: python

    _api_key = pyro.get_properties(topic='my_topic', key='my_api_key')

Next comes the Twilio section:

.. code:: python

            'twilio': {
                # enter your twilio account SID, auth token, and from number here
                'account_sid': ""
                'auth_token': ""
                'from_number': "+1234567890"
            }

which is where you enter your Twilio account information: SID, auth token, and from number. You can get these from your
Twilio account, at `Twilio's website <http://twilio.com>`__. If you don't have an account, setting it up is easy,
and you can even use it in a trial mode to get started.

Lastly in the applications section is this:

.. code:: python

            # the default max length for a single message segment, per twilio, is 160 chars
            # but you can set this anything under 1600.
            'max_message_length': 160

By default, Twilio will break up any message longer than 160 characters to segments of 160, so that is the default
starting point for ``pyrowire``. Technically, you can send messages up to 1600 characters.

Environment Settings
--------------------
Profiles are what ``pyrowire`` uses to determine environment-specific details such as debug, Redis host, and web host.
The default pyrowire\_config.yaml file includes profiles for three standard environments: ``dev``, ``staging``, and
``prod``. Let's take a look at one of those, ``dev``:

.. code:: python

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

Breaking it down into smaller chunks:

.. code:: python

    PROFILES = {
        'dev': {
          'debug': True

The profiles block is defined by the key ``PROFILES``. So original. One
level down is the keyword ``dev`` indicating the beginning of the dev
profile settings.

The first setting in the block is ``debug``, which is stored as a
boolean. Next comes the Redis block:

.. code:: python

        'redis': {
            'host': 'localhost',
            'port': 6379,
            'database': 0,
            'password': ''
        }

First you have the standard Redis connection properties, ``host``, ``port``, ``database``, and \`\ ``password``. This
should be pretty straightforward...just add your connection details in this section. By default all profiles connect to
localhost, over the standard Redis port, default database, with no password. If a password is provided, it will be used,
but ignored otherwise.

Lastly, we have hostname and port information for where the underlying Flask application will run:

.. code:: python

        # set to '0.0.0.0' for Heroku deployment so pyrowire listens on all interfaces
        'host': 'localhost',
        # set to 0 for Heroku deployment so pyrowire can pick up the environment var $PORT
        'port': 5000

Heroku-specific host settings
-----------------------------
Of note is that for Heroku deployment, you will want to set the port to ``0``, which tells ``pyrowire`` to set the port
to the value of the Heroku web container's $PORT env var. Additionally, it is a good idea to set the host for any Heroku
deployments to ``0.0.0.0`` so that ``pyrowire`` will listen on all bindings to that web container.
