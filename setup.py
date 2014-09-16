from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyrowire',
    version='0.1.0',
    description='Super-fast Twilio SMS response API',
    long_description=long_description,
    url='https://github.com/wieden-kennedy/pyrowire',
    author='Wieden+Kennedy Lodge, PDX',
    maintainer='Keith Hamilton',
    maintainer_email='keith.hamilton@wk.com',
    license='BSD License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
       ],
    keywords='api flask framework sms web messaging twilio redis',
    packages=find_packages(exclude=['contrib', 'docs', 'test*', 'bin', 'include', 'lib', '.idea']),
    install_requires=['Flask', 'gunicorn', 'redis', 'twilio'],
    package_data={
        'pyrowire.resources.sample': ['my_settings.py', 'my_app.py', 'Procfile', 'requirements.txt'],
        'pyrowire.resources.console_scripts': ['console_scripts.py']
    },
    data_files=[],
    entry_points={
        'console_scripts': [
            'pyrowire=pyrowire.resources.console_scripts.console_scripts:main',
        ]
    }
)