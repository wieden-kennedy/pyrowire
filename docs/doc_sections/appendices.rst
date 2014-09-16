
APPENDICES
==========

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

    message_data = {'message': 'Original SMS from sender', 'number': '+1234567890',
                    'final_message': 'Right back at ya.'}
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


Appendix C: The Anatomy of a pyrowire Message
---------------------------------------------
Messages in ``pyrowire``  that are available to you in handlers have the following format (sample data presented):

.. code:: python

    # properties marked with an asterisk are those that Twilio will try to collect,
    # and will be included in the message_data dictionary if available.
    message_data = {
        'message': 'Some message',
        'number': '+1234567890',
        'sid': 'ugJCgMZwjxzqGjmrmWhXlyAPbnoTECjEHA',
        'topic': 'some_topic',
        'from_country': 'USA',       *
        'from_state': 'OR',          *
        'from_city': 'Portland',     *
        'from_zip': '97209',         *
        'media': {
            'count': 1,
            'media': {
                'http://bit.ly/Icd34Ox': 'image/jpeg'
            }
        }
    }

Of note here is the media sub-dictionary. If an MMS with attached media was sent, this will be populated with key/value
pairs of the media URL as well as the media content type. If no media was attached (SMS) this key will be an empty dict.

Appendix D: Under the Hood
--------------------------
``pyrowire`` is built on top of the following:

* Flask - handles web server process and request routing
* Twilio REST API - handles communication to and from Twilio
* Redis - used for queuing, and storing received, pending, and completed message transactions

Appendix E: Pull Requests
-------------------------
We love the open source community, and we embrace it. If you have a pull request to submit to ``pyrowire``, do it! Just please
make sure to observe the following guidelines in any additions/updates you wish to merge into the master branch:

* use idiomatic python - we may ask you to resubmit if code does not follow PEP or is "un-pythonic" in nature.
* docstrings required in all methods (*except stuff like getters/setters, stuff that is built-in, or has tests already*)
* unittests required for any added/modified code

Other than that, we welcome your input on this project!

Appendix F: Road Map
--------------------
pyrowire is certainly in its infancy. Thus far, we have a fairly rigid architecture design, and support only for SMS/MMS.
Future endeavors include:

  * providing voice call/queue support
  * building connectors for different message queues (currently only Redis supported)
  * add support for creating additional routes, for web views
  * history management (visibility into Redis database from web view)

If you are into this, and want to help, fork it!
