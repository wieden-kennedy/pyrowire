Running
=======
Once you have all your handlers, validators, and configuration vars in place, it's time to get busy.

Environment Variables
---------------------
pyrowire requires one environment var to be present when running locally:

- **ENV**: the run profile (DEV\|STAGING\|PROD) under which you want to run pyrowire

For running on Heroku, there are two additional environment vars required:

- **RUN**: (WEB\|WORKER), the type of Heroku dyno you are running.
- **TOPIC**: only required for workers, this is the topic the specific worker should be working for.

See `below <#procfile>`__ for more details.

Standalone vs Web vs Worker
---------------------------
pyrowire is designed to be able to run in one of three modes:
  * **standalone**: In standalone mode, at least two threaded processes are started, one for the web application, and one worker process for each topic included in your settings file.
  * **web**: In web mode, only the web application is started. This is most commonly used in Heroku deployment, and can be achieved by including ``RUN=WEB`` in your environment variables.
  * **worker**: In worker mode, only a worker process is started. This also is most commonly used in Heroku deployment, and can be achieved by including both ``RUN=WORKER`` and ``TOPIC=[some-topic]`` in your environment variables.

Running Locally
---------------
Typically, when running locally, pyrowire will run in standalone mode.
Once you have your handler, optional additional validator(s), and configuration all set up, running pyrowire is easy:

::

    ENV=DEV python app.py

This will spin up one worker for your topic (or one per topic if you have multiple topics configured),
and a web server running on localhost:62023 to handle incoming messages. After that, you can start sending it GET/POST
requests using your tool of choice. You won't be able to use Twilio for inbound messages yet,
(unless your local DNS name is published to the world) but you should receive them back from requests made locally.

A Note on Deployment
--------------------
When we built pyrowire, we designed it to be deployed to Heroku; however, pyrowire could certainly be deployed to any
hosted service where separation of concern is possible.

For example, on AWS, pyrowire could easily be run as a set of three EC2 instances (minimally):

    * EC2 instance for web application
    * EC2 instance for a topic worker
    * EC2 instance for Redis

Again, we built it for Heroku, but with a little thought, it can be run anywhere.

Heroku Deployment
-----------------
When you are ready to move to staging or production, it's time to get the app up into Heroku. Remember, the
host setting should be ``0.0.0.0`` and the port setting for your profile should be ``0`` when deploying to Heroku.
You can get through 90% of the work by running:

::

    pyrowire --deploy-heroku

from the root of your project directory.

This will walk you through logging into your Heroku account, if you haven't already, setting up an app, if you haven't already,
and adding Redis as an addon, if you haven't already. It will take you all the way to the point where you will just need to
add any changes to git, commit, and push to Heroku.

Deploying to Heroku Manually
----------------------------
If you would like to set your Heroku stuff up manually, that's totally up to you. We won't get deep into how to manually
deploy to Heroku here,  since it isn't really in the scope of this document, but the basics are:

#. Set up a Heroku application with at least one web dyno and at least one worker.
#. Set up a Redis database as a Heroku add-on, such as RedisToGo or RedisCloud, through a service, such as RedisLabs, or on an external server.
#. Add the Redis host, port, database, and password information to your config file for Staging and/or Production profiles.
#. Add the heroku remote git endpoint to your project (``git remote add heroku.com:my-heroku-app.git``).
#. Push the project up to heroku and let it spin up.
#. Add the remote endpoint to your Twilio account number (e.g., for SMS: ``http://my-heroku-app.herokuapp.com/queue/my_topic``).
#. Profit.

Heroku Procfile
---------------
When you ran ``pyrowire --init`` a sample Procfile was placed in the root of your application folder. Taking a look at it, you can see:

::

    web: ENV=STAGING RUN=web python ./app.py --server run_gunicorn 0.0.0.0:$PORT --workers=1
    worker: ENV=STAGING RUN=worker TOPIC=my_topic python ./app.py

You will need to include a ``RUN`` environment var set to either ``web`` or ``worker`` with respect to the purpose of the command item.

For workers, a ``TOPIC`` environment var is required to indicate which topic the worker(s) should work for.
You can see in the ``web`` line, the default setting in the Procfile is one worker. Scale as needed.

If you would like to run pyrowire for more than one topic, you will need to add additional worker definitions accordingly. For example:

::

    worker: ENV=STAGING RUN=worker TOPIC=my_topic python ./app.py
    worker: ENV=STAGING RUN=worker TOPIC=my_other_topic python ./app.py


