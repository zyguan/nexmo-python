import hashlib
import hmac
import jwt
import os
import time
import uuid
import sys
import warnings

import requests

from .auth import (CredentialsCollection, SecretCredentials,
                   SignatureCredentials, PrivateKeyCredentials)
from .core import Config
from .exceptions import ClientError, ServerError, AuthenticationError
from .sms import SMSProvider

__version__ = '2.0.0'

string_types = (str, bytes)


class Client(object):
    def __init__(self,
                 key=None,
                 secret=None,
                 signature_secret=None,
                 application_id=None,
                 private_key=None,
                 **kwargs):
        self.api_key = key or os.environ.get('NEXMO_API_KEY', None)
        self.api_secret = secret or os.environ.get('NEXMO_API_SECRET', None)
        self.signature_secret = signature_secret or os.environ.get(
            'NEXMO_SIGNATURE_SECRET', None)
        self.application_id = application_id
        self.private_key = private_key
        if isinstance(self.private_key,
                      string_types) and '\n' not in self.private_key:
            with open(self.private_key, 'rb') as key_file:
                self.private_key = key_file.read()

        self.host = 'rest.nexmo.com'

        self.api_host = 'api.nexmo.com'

        self.auth_params = {}

        # Initialize new auth framework:
        auth_collection = CredentialsCollection()
        if self.api_secret:
            auth_collection.append(
                SecretCredentials(self.api_key, self.api_secret))
        if self.signature_secret:
            auth_collection.append(
                SignatureCredentials(self.api_key, self.signature_secret))
        if self.application_id:
            auth_collection.append(
                PrivateKeyCredentials(self.application_id, self.private_key))

        self.config = Config(auth_collection, __version__,
                             kwargs.get('app_name'), kwargs.get('app_version'))

        self.sms = SMSProvider(self.config)

    @property
    def user_agent(self):
        return self.config.user_agent

    @user_agent.setter
    def user_agent(self, value):
        self.config.user_agent = value

    @property
    def headers(self):
        return self.config.headers

    @headers.setter
    def headers(self, value):
        self.config.headers = value

    def check_signature(self, params):
        params = dict(params)

        signature = params.pop('sig', '')

        return hmac.compare_digest(signature, self.signature(params))

    def signature(self, params):
        md5 = hashlib.md5()

        for key in sorted(params):
            md5.update('&{0}={1}'.format(key, params[key]).encode('utf-8'))

        md5.update(self.signature_secret.encode('utf-8'))

        return md5.hexdigest()

    def parse(self, host, response):
        if response.status_code == 401:
            raise AuthenticationError
        elif response.status_code == 204:
            return None
        elif 200 <= response.status_code < 300:
            return response.json()
        elif 400 <= response.status_code < 500:
            message = "{code} response from {host}".format(
                code=response.status_code, host=host)
            raise ClientError(message)
        elif 500 <= response.status_code < 600:
            message = "{code} response from {host}".format(
                code=response.status_code, host=host)
            raise ServerError(message)
