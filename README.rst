pyrowire
========

Super-fast Twilio SMS response API
----------------------------------

``pyrowire`` is an API that handles all of the plumbing necessary to create an SMS message response project with Twilio.
After installing ``pyrowire``, all you have to do is decide what you want to do with the data that comes in to your
web server. We've got the rest covered.

License Info
~~~~~~~~~~~~
This repository is licensed under the BSD 3-Clause license. You can view the license
`here <https://github.com/wieden-kennedy/pyrowire/blob/master/LICENSE>`_

Contents
~~~~~~~~
- `Installation <#1-minute-installation-and-setup>`_
- `Usage <#usage>`_
- `Sample Application <#sample-application>`_
- `One Instance, Many Topics <#one-instance-many-topics>`_
- `Handlers <#handlers>`_
- `Message Validators <#message-validators>`_
- `Overriding Validators <#overriding-validators>`_
- `App Configuration <#setting-up-a-configuration>`_
- `Topics <#topics>`_
- `Profiles <#profiles>`_
- `Heroku-specific Host Settings <#heroku-specific-host-settings>`_
- `Running the app <#running-pyrowire>`_
- `Environment vars <#environment-vars>`_
- `Standalone/Dev mode <#standalonedev>`_
- `Heroku <#heroku>`_
- `Heroku Procfile <#heroku-procfile>`_
- `Sample Application - SMS Randomizer <#full-sample-application>`_
- `Appendix A: Definition of Terms <#appendix-a-definition-of-terms>`_
- `Appendix B: Command Reference <#appendix-b-command-reference>`_
- `Appendix C: Under the Hood <#appendix-c-under-the-hood>`_
- `Appendix D: Pull Requests <#appendix-d-pull-requests>`_


1-Minute Installation and Setup
-------------------------------

``pyrowire`` can be installed and initialized via pip, and is best used with virtualenv. From the root directory of your project, run:

::

    pip install pyrowire && pyrowire-init


| This will install ``pyrowire``, and copy into the root folder the following files:

* `my\_app.py <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/my_app.py>`_ (the application file)
* `my\_settings.py <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/my_settings.py>`_ (the configuration file)
* `Procfile <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/Procfile>`_ (a Heroku Procfile)
* `requirements.txt <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/requirements.txt>`_ (pip requirements file)

Usage
-----
::

  ENV=(DEV|STAGING|PROD) [RUN=(web|worker)] python my_app.py

Sample Application
------------------
Here's what the my_app.py file (created by running ``pyrowire-init``) looks like:

.. code:: python

    import pyrowire
    import my_settings

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

As you can see, it's rather straightforward; to start out you are given placeholders for both a handler and a validator.
The handler is where you will write the business logic for your Twilio application, and additional validators can be added
if needed, or removed altogether. See their respective sections for more information.

Once you have those, there are three steps to configuring your app:

1. `implement a handler for your application topic (required) <#handlers>`_
2. `add any message validators you need (optional) <#message-validators>`_
3. `configure your settings <#settings-configuration>`_


One Instance, Many Topics
-------------------------

``pyrowire`` uses a topic-based approach to handling incoming messages. One ``pyrowire`` instance can scale to handle
many, many different Twilio SMS applications, and separates logic for each by the use of topics. Each topic is
considered to be a separate Twilio application, has its own definition in your config file, and has the endpoint:
::

    http(s)://my-rad-pyrowire-instance.mydomain.com/queue/topic

where ``topic`` is a keyword of your choice that identifies messages as being for a specific application.

Because ``pyrowire`` handles incoming messages, and can assign workers, on a per-topic basis, you could run as many
different applications off of one cluster as you want, provided you scale up for it. Every time a message is received
via Twilio's REST interface, it will be forwarded to your pyrowire instance, queued by its topic, then routed to,
and processed by, a handler specifically designed for that topic/application. Business logic across applications can vary
as much as you need it to, as each topic is handled by a different handler that you define.

Now that you know about ``pyrowire``'s topic-based approach to separation of logic and scaling, let's get into how you
process incoming messages.

Handlers
--------

With ``pyrowire``, the only logic you need to think about (other than optional message validators), is your handler: what
happens to the message after it's been successfully received.

A handler is just a function that defines the business logic for your application, and is annotated
``@pyrowire.handler(topic='whatever_topic_it_is_for')``, where 'whatever_topic_its_for' corresponds to a defined topic
block in your `settings file <#settings-configuration>`_.

Let's take a look at a very simple handler that just receives an incoming message, randomizes the order, then returns it:

.. code:: python

    # all app.handler methods need to be annotated with the topic for which they process
    # and take one kwarg, 'message_data'
    @pyrowire.handler(topic='sms_randomizer')
    def my_handler(message_data=None):
        import random
        # randomize the message and save it as 'return_message'
        message = message_data['message'].split()
        random.shuffle(message)
        message_data['return_message'] = ' '.join(message)

        # send the message data back along with the key of the message body
        # to send to initiate a Twilio SMS reply
        pyrowire.sms(data=message_data, key='return_message')

As you can see, all we need to do to process and return a message is tell a method annotated with
``@pyrowire.handler``(topic='my_topic_name')``  what to do with the message data that is received from the pyrowire app
worker, then send it using ``pyrowire.sms`` method.  To use this method, we pass both the message_data dict object,
as well as the key we want ``pyrowire`` to use to return a message to its sender.

Message Validators
------------------

``pyrowire`` has three default message validators:

- **profanity**: checks the incoming message against a list of about 1,000 graphically profane terms (trust us).
- **length**: checks that the length of the incoming message does not exceed some threshold; Twilio, by default, uses 160 characters as a limit, so we do too. Also ensures incoming messages have a length > 0.
- **parseable**: Twilio can't parse everything. Take emoji for example. The default parseable validator allows inclusion of all alphanumeric characters and most punctuation characters (the ones people actually use in writing, at any rate).

You can define a validator function easily:

1. In your app file, use the ``@pyrowire.validator`` annotation to designate a validator as something that a message needs to be validated against.
2. Add it to your `settings <#settings-configuration>`__ for the topic that requires that validator.

Let's check it out by creating, say, a validator that requires the word 'yo' be present in all messages:

.. code:: python

    # all app.validator methods need to be annotated with the name of the validator
    # and take one kwarg, 'message_data'
    @pyrowire.validator(name='must_include_yo')
    def must_include_yo(message_data=None):
        import re.search
        return not re.search(r'*yo*', message_data['message'].lower())

By using the ``@pyrowire.validator`` annotation, any twilio applications you define in `your configuration file <#settings-configuration>`__
that require the validator 'must\_include\_yo' will have to pass this validator in addition to the three defaults. By convention,
the name of the method should match the name passed into the ``@pyrowire.validator`` decorator, but it doesn't have to.

Overriding Validators
~~~~~~~~~~~~~~~~~~~~~

Say you don't care about profanity. It happens. Say you want to override the default profanity validator, to make it
non-existent—just remove it from your configuration file for the application in question
(see `Applications <#applications>`__ for more info on removing default validators).
If you want to change the validator's behavior, just define it again:

.. code:: python

    # profanity validator that considers 'reaver' to be the only bad word in the verse
    @pyrowire.validator
    def profanity(message_data=None):
        import re.search
        return re.search(r'\breaver\b', message_data['message'].lower())

Settings configuration
----------------------

Once you've got your validators and handlers set up, you'll need to dial in your config file. ``pyrowire`` uses a python file for settings configuration.
for its configuration files. To check out the sample settings file, look
`here <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/my_settings.py>`_. pyrowire's configuration files are broken down into two sections:

- **Topics** (Twilio application-specific settings). The Topics block can have as many topic dictionaries are are needed.
- **Profiles** (environment profile-specific settings). There is one block per run environment *(DEV/STAGING/PROD)*

Topics
~~~~~~
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

            # the default max length for a message per twilio is 160 chars, but you can set this anything under that.
            'max_message_length': 160

By default, Twilio will break up any message longer than 160 characters to segments of 160, so that is the default
starting point for ``pyrowire``. Technically, you can send messages up to 1600 characters.

Profiles
~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Of note is that for Heroku deployment, you will want to set the port to ``0``, which tells ``pyrowire`` to set the port
to the value of the Heroku web container's $PORT env var. Additionally, it is a good idea to set the host for any Heroku
deployments to ``0.0.0.0`` so that ``pyrowire`` will listen on all bindings to that web container.

Running pyrowire
----------------

So you have all your handlers, validators, and configuration vars in
place. Time to run ``pyrowire``. Here's what you need to know.

Environment vars
~~~~~~~~~~~~~~~~

``pyrowire`` requires one environment var to be present when running locally:

- **ENV**: the run profile (DEV\|STAGING\|PROD) under which you want to run ``pyrowire``

For running on Heroku, there are two additional environment vars required:

- **RUN**: (web\|worker), the type of Heroku dyno you are running. 
- **TOPIC**: only required for workers, this is the topic the specific worker should be working for.

See `below <#procfile>`__ for more details.

Standalone/Dev
~~~~~~~~~~~~~~

Once you have your handler, optional additional validator(s), and configuration all set up, running ``pyrowire`` is easy:

::

    ENV=DEV python my_app.py

This will spin up a worker for your topic(s), and a web server running on localhost:5000 to handle incoming messages.
After that, you can start sending it GET/POST requests using your tool of choice. You won't be able to use Twilio for
inbound messages yet, (unless your local DNS name is published to the world) but you should receive them back from requests made locally.

Heroku
~~~~~~

Right, so. When you are ready to move to staging or production, it's time to get the app up into Heroku. Remember, the
host setting should be ``0.0.0.0`` and the port setting for your profile should be ``0`` when deploying to Heroku.
We won't get deep into how to deploy to Heroku here, since it isn't really in the scope of this document, but the basics
are:

#. Set up a Heroku application with at least one web dyno and at least one worker.
#. Set up a Redis database as a Heroku add-on, such as RedisToGo or RedisCloud, through a service, such as RedisLabs, or on an external server.
#. Add the Redis host, port, database, and password information to your config file for Staging and/or Production profiles.
#. Add the heroku remote git endpoint to your project (``git remote add heroku.com:my-heroku-app.git``).
#. Push the project up to heroku and let it spin up.
#. Add the remote endpoint to your Twilio account number (e.g., for SMS: ``http://my-heroku-app.herokuapp.com/queue/my_topic``).
#. Profit.

Heroku Procfile
~~~~~~~~~~~~~~~

When you ran ``pyrowire-init`` a sample Procfile was placed in the root of your application folder. Taking a look at it, you can see:

::

    web: ENV=STAGING RUN=web python ./my_app.py --server run_gunicorn 0.0.0.0:$PORT --workers=1
    worker: ENV=STAGING RUN=worker TOPIC=my_topic python ./my_app.py

You will need to include a ``RUN`` environment var set to either ``web`` or ``worker`` with respect to the purpose of the command item.

For workers, a ``TOPIC`` environment var is required to indicate which topic the worker(s) should work for.
You can see in the ``web`` line, the default setting in the Procfile is one worker. Scale as needed.

Full Sample Application
-----------------------
For a full sample application, check out the official `gist <https://gist.github.com/keithhamilton/457a72089e80d9238508>`_
where an SMS shuffler is created to randomize incoming text messages and send them back to their senders.

Appendix A: Definition of Terms
-------------------------------
Handler
~~~~~~~
A handler is one of the fundamental building blocks of ``pyrowire``. It is responsible for the business logic performed for
an application, and determines how ``pyrowire`` will respond to an inbound message via Twilio's REST API. Applications and
handlers have a unique one-to-one relationship.

Handlers can be added by annotating a method with ``@pyrowire.handler(topic='some_topic_name'), where 'some_topic_name'
corresponds to an application to be handled by ``pyrowire``.

Validator
~~~~~~~~~
A validator is another fundamental building block of ``pyrowire``. Validators are responsible for validating incoming messages, and
unlike handlers, are optional. Validators have a many-to-one relationship with applications.

Validators can be added to any application by creating a method annotated with
``@pyrowire.validator(name='some_validator_name')`` and adding that validator as a key/value member of the application's ``validators``
set in your ``pyrowire_config.yaml`` file.

Each validator added to an application should have a corresponding message, e.g, 'must_say_yo': 'You got to say "yo", yo!'

Appendix B: Command Reference
-----------------------------
A reference for the most commonly-used methods in creating a ``pyrowire`` app.

pyrowire.configure(settings=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A new pyrowire app can be configured using the pyrowire.configure() method, which takes one kwarg, ``settings``.

.. code:: python

    import my_settings
    pyrowire.configure(settings=my_settings)


pyrowire.sms(data=None, key=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To return an SMS back to its sender, you will use the pyrowire.sms method, which takes two kwargs:

#. ``data``: the message_data (dict) that was initially passed to the handler method
#. ``key``: the key for the dict that contains the processed message to return to the sender.

Example:

.. code:: python

    message_data = {'message': 'Original SMS from sender', 'number': '+1234567890', 'final_message': 'Right back at ya.'}
    pyrowire.sms(data=message_data, key='final_message')

pyrowire.run()
~~~~~~~~~~~~~~
Runs the pyrowire application. Depending on environment variables, will do one of three things:
#. If RUN environment variable is not present, will start a worker process for each topic defined in your configuration file,
then start a web server to receive inbound messages.
#. If the RUN environment variable is present, and set to ``web``, will start a web server process to receive inbound messages.
#. If the RUN environment variable is present, and set to ``worker``, will start a worker process to process messages once received and queued.

Using Handlers
~~~~~~~~~~~~~~
Handlers can be named whatever you prefer, but must satisfy three requirements:

#. They must be annotated with ``@pyrowire.handler``
#. The annotation must be passed a kwarg, ``topic``, and should be set equal to the topic/application for which it is intended to process messages.
#. The handler function itself must take one kwarg, ``message_data``, and should be set to ``None`` as a default.

Example:

.. code:: python

    import my_settings
    pyrowire.configure(settings=my_settings)

    @pyrowire.handler(topic='my_cool_topic')
    def my_cool_handler(message_data=None):
        message_data['final'] = message_data['message']
        my_cool_pyro_app.sms(data=message_data, key='final')


Using Validators
~~~~~~~~~~~~~~~~
Validators, too, can be named whatever you prefer, but must satisfy three requirements:

#. They must be annotated with ``@pyrowire.validator``
#. The annotation must be passed one kwarg, ``name``, and should be set to the name of the validator as entered in your configuration
    file for the application that requires it.
#. The validator function itself must take one kwarg, ``message_data``, and should be set to ``None`` as a default.

Example:

.. code:: python

    import my_settings
    pyrowire.configure(settings=my_settings)

    @pyrowire.validator(name='my_validator')
    def some_validator(message_data=None):
        import re
        # returns True if message does not contain the substring 'yo'
        return not re.search(r'\byo\b', message_data['message'].lower())


Appendix C: Under the Hood
--------------------------
``pyrowire`` is built on top of the following:

* Flask - handles web server process and request routing
* Twilio REST API - handles communication to and from Twilio
* Redis - used for queuing, and storing received, pending, and completed message transactions

Appendix D: Pull Requests
-------------------------
We love the open source community, and we embrace it. If you have a pull request to submit to ``pyrowire``, do it! Just please
make sure to observe the following guidelines in any additions/updates you wish to merge into the master branch:

* use idiomatic python - we may ask you to resubmit if code does not follow PEP or is "un-pythonic" in nature.
* docstrings required in all methods (*except stuff like getters/setters, stuff that is built-in, or has tests already*)
* unittests required for any added/modified code

Other than that, we welcome your input on this project!
