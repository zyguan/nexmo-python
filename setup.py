import re

from setuptools import setup

setup(
    name='nexmo',
    version='2.0.0-dev',
    description='Nexmo Client Library for Python',
    long_description='This is the Python client library for Nexmo\'s API. \
 To use it you\'ll need a Nexmo account. \
 Sign up `for free at nexmo.com <http://nexmo.com?src=python-client-library>`_.',
    url='http://github.com/Nexmo/nexmo-python',
    author='Nexmo Developer Relations',
    author_email='devrel@nexmo.com',
    license='MIT',
    packages=['nexmo'],
    platforms=['any'],
    install_requires=[
        'PyJWT          ~= 1.5.3',
        'cryptography   ~= 2.1.4',
        'attrs          ~= 17.2.0',
        'marshmallow    ~= 3.0.0b7',
        'aiohttp        ~= 2.3.10',
        'requests       ~= 2.18.4',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ])
