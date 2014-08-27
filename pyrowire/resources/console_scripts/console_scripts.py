#!/usr/bin/python
import os
import re
import shutil


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
        shutil.copy(os.path.join(source_path, file), os.path.join(current_path, f))
        copied_files.append(f)

    print '''\
    \n
    Awesome. You now are ready to start using pyrowire. To get you started, we've copied the following
    sample files into this folder:
    \n
    ''' + '\n\t'.join('* ./%s' % x for x in copied_files) + \
          'For help on how to get started, check out the README at https://github.com/wieden-kennedy/pyrowire/'


