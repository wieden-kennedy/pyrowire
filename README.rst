pyrowire
========

pyrowire is a framework you can use to quickly create Twilio-based SMS/MMS applications, licensed under the BSD 3-Clause license.

Quickstart
==========
*For the purposes of this quickstart, it is assumed that you have an account with both Heroku and Twilio, and that you have at minimum the following installed:*
    * pip
    * virtualenv

In your virtual environment root directory, execute:

::

    $ pip install pyrowire && pyrowire --init

| This will install ``pyrowire``, and copy into the root folder the following files:

* `my\_app.py <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/my_app.py>`_ (the application file)
* `my\_settings.py <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/my_settings.py>`_ (the configuration file)
* `Procfile <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/Procfile>`_ (a Heroku Procfile)
* `requirements.txt <https://github.com/wieden-kennedy/pyrowire/blob/master/pyrowire/resources/sample/requirements.txt>`_ (pip requirements file)

Usage
-----
::

  $ ENV=(DEV|STAGING|PROD) [RUN=(WEB|WORKER)] [TOPIC=] python my_app.py

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

For full documentation and a tutorial, please visit our `documentation page <#>`_.
