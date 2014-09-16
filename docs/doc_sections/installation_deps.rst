Dependencies
============
pip
---
We lean heavily towards pip for installing virtualenv, since ultimately it is our preferred distribution method for pyrowire.
Fortunately, installing pip is super easy.

OS X
~~~~
If you are a Homebrew user, and have installed python with

::

    $ brew install python

you should already have pip on your machine. Otherwise, you can use easy_install:

::

    $ sudo easy_install pip

Linux
~~~~~
To install pip on Linux, you can use the default package manager for your Linux flavor:

::

    $ sudo (yum|apt-get) install python-pip

virtualenv
----------
virtualenv is a great tool for development, because it isolates python versions from the system python version. This is great
for you because it means you can develop your python applications independent of each other, regardless of whether they
require different versions of python and your application's various dependencies.

OS X/Linux
~~~~~~~~~~
Getting virtualenv installed is pretty straightforward, using either easy_install:

::

    $ sudo easy_install virtualenv

or, with pip (our fav):

::

    $ sudo pip install virtualenv

Redis
-----
pyrowire currently has a hard dependency on Redis, so you will need to install that on your dev machine:

OS X
~~~~
Do it with Homebrew (if you don't use Homebrew, you really should check it out):

::

    $ brew install redis

Linux
~~~~~
**Ubuntu/Debian**

::

    $ sudo apt-get install redis-server

**RHEL**

::

    $ sudo yum install redis



