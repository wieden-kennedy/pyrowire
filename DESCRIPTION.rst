pyrowire
========

Fast Twilio SMS message response API
------------------------------------

``pyrowire`` is an API that handles all of the plumbing necessary to create an SMS message response project with Twilio.
After installing ``pyrowire``, all you have to do is decide what you want to do with the data that comes in to your
web server. We've got the rest covered.

**This is a condensed version of the full README, found `here <https://github.com/wieden-kennedy/pyrowire>`_.
For more details, please view the full README.**

License Info
~~~~~~~~~~~~
This repository is licensed under the BSD 3-Clause license. You can view the license
`in the github repo <https://github.com/wieden-kennedy/pyrowire/blob/master/LICENSE>`_

1-minute Installation & Setup
-----------------------------

``pyrowire`` can be installed and initialized via pip, and is best used with virtualenv. From the root directory of your project, run:

::

    pip install pyrowire && pyrowire-init

| This will install ``pyrowire``, and copy into the root folder the following files:

* `my\_app.py <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/sample/my_app.py>`_ (the application file)
* `pyrowire\_config.yaml <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/sample/pyrowire_config.yaml>`_ (the configuration file)
* `Procfile <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/sample/Procfile>`_ (a Heroku Procfile)
* `requirements.txt <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/sample/Profcile>`_ (requirements file to install pyrowire on Heroku)

Usage
-----
::

  PYRO_CONFIG=./rel/path/to/config.yaml ENV=(DEV|STAGING|PROD) [RUN=(web|worker)] python my_app.py

Sample Application
------------------
Here's what the sample app (from running ``pyrowire-init``) looks like:

.. code-block:: python

    from pyrowire.app.pyrowire import PyroApp

    # instantiate the PyroApp object. No parameters required.
    pyro = PyroApp()

    # all app.processor methods need to be annotated with the topic for which they process
    # and take one kwarg, 'message_data'
    @pyro.processor(topic='my_topic')
    def my_processor(message_data=None):
        pass

    # all app.filter methods need to be annotated with the name of the filter
    # and take one kwarg, 'message_data'
    @pyro.filter(name='my_filter')
    def my_filter(message_data=None):
        pass

    if __name__ == '__main__':
        pyro.run()

As you can see, it's rather straightforward; to start out you are given placeholders for both a processor and a filter.
The processor is where you will write the business logic for your Twilio application, and additional filters can be
added if needed, or removed altogether. See their respective sections for more information.

Configuration
-------------
Once you've run the install and setup, there are three steps to configuring your app:

1. Implement a processor (required)
2. Add any additional filters for incoming messages (optional)
3. Set up the config file

Processors
----------
With ``pyrowire``, the only logic you need to think about (other than optional message filters), is your processor:
what happens to the message that comes in after it's been successfully received.

A processor is just a function that define the business logic for your application, and is annotated
``@processor(topic='whatever_topic_it_is_for')``, where 'whatever_topic_its_for' corresponds to a defined application
block in your application configuration file. Let's take a look at a very simple processor, that just receives an
incoming message, randomizes the order, then saves it:

.. code-block:: python

    # all app.processor methods need to be annotated with the topic for which they process
    # and take one kwarg, 'message_data'
    @pyro.processor(topic='my_topic')
    def my_processor(message_data=None):
        import random
        # randomize the message and save it as 'return_message'
        message = message_data['message'].split()
        random.shuffle(message)
        message_data['return_message'] = ' '.join(message)

        # send the message data back along with the key of the message body
        # to send to initiate a Twilio SMS reply
        pyro.sms(data=message_data, key='return_message')

As you can see, all we need to do to process and return a message is tell a method annotated with
``@pyro.processor``(topic='my_topic_name')`` what to do with the message data that is received from the pyrowire app
worker, then send it using ``pyro.sms`` method. To use this method, we pass both the message_data dict object,
as well as the key we want ``pyrowire`` to use to return a message to its sender.

Message Filters
---------------

``pyrowire`` has three default message filters: **profanity**, **length**, and **parseable**.

You can define additional filter functions easily:

1. In your app file, use the ``@filter`` annotation to designate a filter as something that a message needs
to be validated against.
2. Add it to your configuration for the topic that requires that filter.

Let's check it out by creating, say, a filter that requires the word 'yo' be present in all messages:

.. code-block:: python

    # all app.filter methods need to be annotated with the name of the filter
    # and take one kwarg, 'message_data'
    @pyro.filter(name='must_include_yo')
    def must_include_yo(message_data=None):
        import re.search
        return not re.search(r'*yo*', message_data['message'].lower())

Setting up a configuration
--------------------------

``pyrowire's`` configuration files are broken down into two sections: **Applications** and **Profiles**

Applications
~~~~~~~~~~~~

Here's what the application section of a ``pyrowire`` config file looks like:

::

    applications:
        my_topic:
          # send_on_accept determines whether to send an additional accept/success
          # message upon successfully receiving and SMS
          # NOTE: this will result in two return messages per inbound message
          send_on_accept: False
          # these are global accept (success) and error messages for your app
          accept_response: "Great, we'll get right back to you."
          error_response: "It seems an error has occurred...sorry about that."
          filters:
            # define your specific filters here. If you change one of the below messages
            # you don't need to do anything else.
            # if you want to add a filter, you will need to implement a @filter method in your application file
            profanity: "You kiss your mother with that mouth? No profanity, please."
            length: "Your message exceeded the maximum allowable character limit. Try something shorter."
            parseable: "Please only use alphanumeric and punctuation characters. No emoji!"
          properties:
            # add in any additional properties, such as API keys for other services, here
          twilio:
            # enter your twilio account SID, auth token, and from number here
            account_sid: ""
            auth_token: ""
            from_number: "+1234567890"
          # the default max length for a single message segment, per twilio, is 160 chars
          # but you can set this anything under 1600.
          max_message_length: 160

Profiles
~~~~~~~~

Profiles are what ``pyrowire`` uses to determine environment-specific details such as debug, Redis host, and web host.
This is what the default ``dev`` profile looks like:

::

    # application stuff here ...
     profiles:
        dev:
          debug: True
          redis:
            host: "localhost"
            port: 6379
            database: 0
            password: ""
          host: "localhost"
          port: 5000

Heroku-specific host settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Of note is that for Heroku deployment, you will want to set the port to ``0``, which tells ``pyrowire`` to set the port
to the value of the Heroku web container's $PORT env var. Additionally, it is a good idea to set the host for any Heroku
deployments to ``0.0.0.0`` so that ``pyrowire`` will listen on all bindings to that web container.


Environment vars
~~~~~~~~~~~~~~~~

``pyrowire`` requires two environment vars to be present when running:

- **PYRO\_CONFIG**: the path to your config file
- **ENV**: the run profile (DEV\|STAGING\|PROD) under which you want to run ``pyrowire``

For running on Heroku, there are two additional environment vars required:

- **RUN**: (web\|worker), the type of Heroku dyno you are running. 
- **TOPIC**: only required for workers, this is the topic the specific worker should be working for.

See Heroku Procfile for more details.

Standalone/Dev
~~~~~~~~~~~~~~

Once you have your processor, optional additional filter(s), and configuration all set up, running ``pyrowire`` is easy:

::

    PYRO_CONFIG=./pyro_config.yaml ENV=DEV python my_app.py

This will spin up a worker for your topic(s), and a web server running on localhost:5000 to handle incoming messages.
After that, you can start sending it GET/POST requests using your tool of choice. You won't be able to use Twilio for
inbound messages yet, (unless your local DNS name is published to the world) but you should receive them back from requests made locally.

Heroku
~~~~~~

Right, so. When you are ready to move to staging or production, it's time to get the app up into Heroku. Remember, the
host setting should be ``0.0.0.0`` and the port setting for your profile should be ``0`` when deploying to Heroku.
We won't get deep into how to deploy to Heroku here, since it isn't really in the scope of this document, but the basics
are:

#. Set up a Heroku application with at least one web dyno and at least one worker
#. Set up a Redis database on an external server, through a service, or as an add-on
#. Add the Redis host, port, database, and password information to your config file for Staging and/or Production profiles.
#. Add the heroku remote git endpoint to your project (``git remote add heroku.com:my-heroku-app.git``)
#. Push the project up to heroku and let it spin up.
#. Add the remote endpoint to your Twilio account number (e.g., for SMS: ``http://my-heroku-app.herokuapp.com/queue/my_topic``)
#. Profit.

Heroku Procfile
~~~~~~~~~~~~~~~

When you ran ``pyrowire-init`` a sample Procfile was placed in the root of your application folder.
Taking a look at it, you can see:

::

    web: ENV=STAGING RUN=web python ./my_app.py --server run_gunicorn 0.0.0.0:$PORT --workers=1
    worker: ENV=STAGING RUN=worker TOPIC=my_topic python ./my_app.py

You will need to include a ``RUN`` environment var set to either ``web`` or ``worker`` with respect to
the purpose of the command item.

For workers, you will additionally need to include a ``TOPIC`` environment var to indicate which topic the worker(s)
should work for. You can see in the ``web`` line, the default setting in the Procfile is one worker. Scale as needed.

Sample Application
------------------
For a full sample application, check out the official `gist <https://gist.github.com/keithhamilton/457a72089e80d9238508>`_
where an SMS shuffler is created to randomize incoming text messages and send them back to their senders.

Source Code
-----------
The full source code for ``pyrowire``, and tests, can be found at the `github repo <https://github.com/wieden-kennedy/pyrowire>`_
