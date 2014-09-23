Settings
========
Once you have your validators and handlers set up, you'll need to dial in your settings file.

pyrowire uses a python file for settings configuration. To check out the sample settings file, look
`here <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/settings.py>`_.

pyrowire's settings files are broken down into two sections:

- **Topics** (Twilio application-specific settings). The Topics block can have as many topic dictionaries as are needed.
- **Profiles** (environment profile-specific settings). There is one block per run environment *(DEV/STAGING/PROD)*

Defining a Topic
----------------
To start out, here's what the topic section of a pyrowire settings file looks like:

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

This is the beginning of the applications dictionary, and, we have defined one topic, ``my_topic``.

Response Settings
~~~~~~~~~~~~~~~~~

.. code:: python

    # send_on_accept determines whether to send an additional accept/success message upon
    # successfully receiving an SMS.
    # NOTE: this will result in two return messages per inbound message
    'send_on_accept': False,
    # global accept (success) and error messages for your app
    'accept_response': 'Great, we\'ll get right back to you.',
    'error_response': 'It seems like an error has occurred...please try again later.',


*  **send\_on\_accept** enables or disables your app from actually sending a reply message
   immediately after the incoming SMS was successfully accepted. Setting this to ``False``
   will prevent your app from sending two return messages for every one it receives.
*  **accept\_response** and **error\_response** are respectively the messages that will be
   returned in the event of a success or error.
   *Note:* error\_response will always send if an error occurs.

Validator Settings
~~~~~~~~~~~~~~~~~~
**profanity**, **length**, and **parseable** are the default validators for your app. To omit any one of these, comment out or
remove the item from the application's validators definition. Changing the message will change the return message sent to
the user if his/her message fails to pass the validator.

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

It is in the ``validators`` block that you would add any custom validators and their respective fail messages if you add validators to your
application. Remember, excluding a validator from an app config will cause it to not be used on any incoming messages for
that application; this means you can selectively apply different validators to different applications.

Properties Settings
~~~~~~~~~~~~~~~~~~~
Properties are used for very specific application purposes. Say you want to translate all incoming messages into
Yoda-speak, and you need to hit an API for that...this is where you can add in your API key. The properties property in
the app config is just a catch-all spot for your application-specific custom properties.

.. code:: python

            # properties are any non-pyrowire-specific properties that you will need to
            # run your handler, such as an API key to some external service.
            'properties': {},


In your handler method, then, you could access this as follows:

.. code: python

    _api_key = config.properties(topic='my_topic', key='my_api_key')

Twilio Settings
~~~~~~~~~~~~~~~
This is where you enter your Twilio account information: SID, auth token, and from number. You can get these from your
Twilio account, at `Twilio's website <http://twilio.com>`__. If you don't have an account, setting it up is easy,
and you can even use it in a free trial mode to get started.


.. code:: python

            'twilio': {
                # enter your twilio account SID, auth token, and from number here
                'account_sid': ""
                'auth_token': ""
                'from_number': "+1234567890"
            }

Maximum Message Length Setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Technically, you can receive messages as long as 1600 characters, but Twilio will break up any message longer than
160 characters to segments of 160. Since 160 characters is the default max for one message segment, it is the default
setting for pyrowire apps.

.. code:: python

            # the default max length for a single message segment, per twilio, is 160 chars
            # but you can set this anything under 1600.
            'max_message_length': 160

Environment Settings
--------------------
pyrowire uses profiles to determine environment-specific details such as debug, Redis host, and web host.
The default settings.py file includes profiles for three standard environments: ``dev``, ``staging``, and
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
            'port': 62023
        }

The profiles block is defined by the key ``PROFILES``. So original. One
level down is the keyword ``dev`` indicating the beginning of the dev
profile settings.

Debug and Logging Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~
The first setting in the block is ``debug``, which is stored as a boolean. Python's ``logging`` module is used to indicate
the logging level for each profile.

.. code:: python

    PROFILES = {
        'dev': {
          'debug': True,
          'log_level': logging.DEBUG,


Redis Settings
~~~~~~~~~~~~~~

.. code:: python

        'redis': {
            'host': 'localhost',
            'port': 6379,
            'database': 0,
            'password': ''
        }

First, you have the standard Redis connection properties, ``host``, ``port``, ``database``, and ``password``. This
should be pretty straightforward...just add your connection details in this section.

By default, all profiles connect to localhost over the standard Redis port using the default database with no password.
If a password is provided, it will be used, but ignored otherwise.


Host and Port Settings
~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

        # set to '0.0.0.0' for hosted deployment so pyrowire listens on all interfaces
        'host': 'localhost',
        # set to 0 for hosted deployment so pyrowire can pick up the environment var $PORT
        'port': 62023

Hosted Deployment Settings
--------------------------
Of note is that for a hosted deployment, you will want to set the port to ``0``, which tells pyrowire to set the port
to the value of the web container's $PORT env var. Additionally, it is a good idea to set the host for any hosted
deployments to ``0.0.0.0`` so that pyrowire will listen on all bindings to that web container.
