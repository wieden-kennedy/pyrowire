pyrowire
========

Fast Twilio SMS message response API
------------------------------------

``pyrowire`` is an API that handles all of the plumbing necessary to create an SMS message response project with Twilio.
After installing ``pyrowire``, all you have to do is decide what you want to do with the data that comes in to your
web server. We've got the rest covered.

Documentation
-------------
For full documentation and a tutorial, please visit our `documentation page <#>`_.

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
Here's what the sample app (from running ``pyrowire-init``) looks like:

.. code-block:: python

    import pyrowire
    import my_settings

    # configure the pyrowire application
    pyrowire.configure(settings=my_settings)

    # all app.handler methods need to be annotated with the topic for which they process
    # and take one kwarg, 'message_data'
    @pyrowire.handler(topic='my_topic')
    def my_handler(message_data=None):
        pass

    # all app.validator methods need to be annotated with the name of the validator
    # and take one kwarg, 'message_data'
    @pyrowire.validator(name='my_validator')
    def my_validator(message_data=None):
        pass

    if __name__ == '__main__':
        pyrowire.run()

As you can see, it's rather straightforward; to start out you are given placeholders for both a handler and a validator.
The handler is where you will write the business logic for your Twilio application. One or more validators can be
added if needed, or removed altogether. See their respective sections below for more information.

