#!/usr/bin/python
import argparse
import os
import re
import shutil
import sys

from fabric.api import *
from fabric.colors import red as _red, green as _green, yellow as _yellow, white as _white
from fabric.utils import abort


def parse_args():
    parser = argparse.ArgumentParser(description="command line args to assist with development")
    parser.add_argument('--init', dest='init', default=None, action='store_true',
                        help='initialize stub files for pyrowire development')
    parser.add_argument('--deploy-heroku', dest='deploy_heroku', action='store_true', default=None,
                        help='deploy current pyrowire project to heroku')
    parser.add_argument('--add-heroku-redis', dest='add_heroku_redis', action='store_true', default=None,
                        help='add redis to an existing heroku deployment')
    return parser.parse_args()


def init():
    """
    executed from command line by typing: pyrowire-init
    copies all stub files to root directory of new pyrowire project.
    """
    current_path = os.getcwd()
    stub_path = 'lib/python2.7/site-packages/pyrowire/resources/sample'
    source_path = os.path.join(current_path, stub_path)

    copied_files = []
    # copy all files from sample folder
    for f in [x for x in os.listdir(source_path) if not re.match(r'^\.|^_|.*pyc$', x)]:
        shutil.copy(os.path.join(source_path, f), os.path.join(current_path, f))
        copied_files.append(f)

    print '''\
    \n
    P    Y    R    O    W    I    R    E
    *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
    *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
    \n
        Awesome. You now are ready to start using pyrowire.
    To get you started, we've copied the following sample files into this folder:
    \n\t
    ''' + \
    '\n    '.join('* ./%s' % x for x in copied_files) + \
    '\n\n\n    For help on how to get started, check out the README at https://github.com/wieden-kennedy/pyrowire/\n' + \
    '''
    *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
    \n
    '''

def check_git():
    if not os.path.exists('.git'):
        local('git init .')

def install_heroku_toolbelt():
    is_installed = False
    install = prompt(_white("Heroku Toolbelt is not installed. Would you like to install it? [n] ")) or None
    if install:
        if re.search('darwin', sys.platform):
            # install with brew if available
            brew = local('which brew', capture=True)
            if brew:
                local('brew install heroku-toolbelt')
                is_installed = True
            else:
                abort(_red("Attempted to install heroku-toolbelt with brew, but brew was not found. "
                           "Please install homebrew and try again, or install the heroku-toolbelt manually "
                           "from https://toolbelt.heroku.com"))

        elif re.search('linux', sys.platform):
            # install with wget if ubuntu
            is_ubuntu = local('uname -v', capture=True)
            if re.search('ubuntu', is_ubuntu.lower()):
                sudo('wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh')
                is_installed = True

    if is_installed:
        print(_green("Heroku Toolbelt successfully installed"))


def heroku_remote_exists():
    remotes = local('git remote -v', capture=True).split('\n')
    return len([i for i in remotes if re.search('heroku', i)]) > 0


def heroku_select_account():
    # select heroku account
    accounts = local('heroku accounts', capture=True) or None
    if accounts:
        return prompt(_white("Type the name of the Heroku account you would like to use:\n\t%s%s\n" %
                             (_yellow('* '), _yellow('\n\t* '.join(accounts.split('\n'))))))

    else:
        add_account = prompt(_white("No heroku toolbelt account was found. Would you like to add one? [n] ")) or None
        if add_account:
            account_name = prompt(_white("Type the name of the account you would like to add"))
            local('heroku accounts:add %s' % account_name)
            return account_name


def heroku_select_or_create_app(account_name):
    account_applications = local('heroku apps --account %s' % account_name, capture=True)
    app = prompt(_white("Type the name of the application you wish to use, or press "
                        "Enter to create a new one:\n\t%s%s\nSelection: " %
                        (_yellow('* '), _yellow('\n\t* '.join(account_applications.split('\n')))))) or None
    if app:
        if app in account_applications:
            return app

    app = prompt(_white("Type the name of the app you would like to create: "))
    local('heroku apps:create %s --account %s' % (app, account_name))
    return app


def heroku_add_redis(app=None, account=None):
    redis_host = None
    redis_port = 6379
    redis_password = None
    redis_db = 0

    if not account:
        account = heroku_select_account()
    if not app:
        app = heroku_select_or_create_app(account)

    redis_exists = local('heroku addons --app %s --account %s' % (app, account), capture=True)
    if not 'redistogo' in redis_exists:
        local('heroku addons:add --app %s --account %s redistogo:nano' % (app, account))

    open_redis_details = prompt(_white("Would you like to open the addon's details in your browser now? [n] ")) or False
    if open_redis_details:
        prompted = prompt(_yellow("Once the redis details open, you will be prompted to enter some details. "
                                  "You can type 'q' at any time to cancel updating your application's Redis details."
                                  "Press Enter to open the Redis details page."))
        if prompted != 'q':
            local('heroku addons:open --app %s --account %s redistogo:nano' % (app, account))
            prompted = prompt(_white("From the 'General' section, paste the name of the redis instance (like 'angelfish-9357')")) or None
        if prompted and prompted != 'q':
            host, redis_port = prompted.strip().split('-')
            redis_host = '%s.redistogo.com' % host
            prompted = prompt(_white("From the security section, paste the Redis password: ")) or None
        if prompted and prompted != 'q':
            redis_password = prompted

    is_staging = prompt(_white("Which environment is this for?\n\t1. Staging\n\t2. Production\nSelection: "))
    profile = 'staging'
    if '2' in is_staging:
        profile = 'prod'
    settings_file = [i for i in os.listdir('./') if re.search('settings', i) and not re.search(r'.*\.pyc$', i)][0]
    settings_path = os.path.join('./', settings_file)

    f = open(settings_path, 'r')
    settings_lines = [
        i.replace('<%s.redis_host>' % profile, redis_host)
            .replace('<%s.redis_port>' % profile, str(redis_port))
            .replace('<%s.redis_password>' % profile, redis_password) for i in f.readlines()]

    f = open('%s' % settings_path, 'w')
    for line in settings_lines:
        f.write(line)
    f.close()


def heroku_deploy():
    if not heroku_remote_exists():
        # check if heroku toolbelt is available
        heroku_bin = local('which heroku', capture=True)
        if not heroku_bin:
            install_heroku_toolbelt()

        # log in to heroku
        selected_account = heroku_select_account()
        local('heroku login --account %s' % selected_account)

        # select or create an app
        app_name = heroku_select_or_create_app(selected_account)

        # add redis ?
        add_redis = prompt(_white("Type 'y' to add Redis To Go to your Heroku application "
                                  "(to use an external service, update your settings file): ")) or None
        if add_redis.lower() == 'y':
            heroku_add_redis(app=app_name, account=selected_account)

        check_git()
        # add git remote
        local('git remote add heroku heroku.com:%s.git' % app_name)

        print(_green("You are ready to commit any changes and deploy to heroku by typing: %s" %
                     _white("git push heroku <name_of_branch>")))
        return None
    print(_green("Looks like there is already a heroku remote set up. Huzzah!"))


def main():
    args = parse_args()
    if args.init:
        init()
    elif args.deploy_heroku:
        heroku_deploy()
    elif args.add_heroku_redis:
        heroku_add_redis(app=None, account=None)




