import hashlib
import hmac
import logging
import os

from platform import python_version
from .auth import (CredentialsCollection, SecretCredentials,
                   SignatureCredentials, PrivateKeyCredentials)
from .core import Sling, RequestsRequester, AioHttpRequester
from .exceptions import ClientError, ServerError, AuthenticationError
from .sms import SMSProvider

__version__ = '2.0.0'

string_types = (str, bytes)


LOG = logging.getLogger('nexmo')


class Client(object):
    def __init__(
            self,
            *,
            key=None,
            secret=None,
            signature_secret=None,
            application_id=None,
            private_key=None,
            app_name=None,
            app_version=None):
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

        # Initialize auth collection:
        creds = CredentialsCollection()
        if self.api_secret:
            LOG.debug("Creating SecretCredentials for: %s", self.api_key)
            creds.append(
                SecretCredentials(self.api_key, self.api_secret))
        if self.signature_secret:
            LOG.debug("Creating SignatureCredentials for: %s", self.api_key)
            creds.append(
                SignatureCredentials(self.api_key, self.signature_secret))
        if self.application_id:
            LOG.debug("Creating PrivateKeyCredentials for app: %s", self.application_id)
            creds.append(
                PrivateKeyCredentials(self.application_id, self.private_key))

        user_agent = 'nexmo-python/{0}/{1}'.format(__version__,
                                                   python_version())
        if app_name is not None and app_version is not None:
            user_agent += '/{0}/{1}'.format(app_name, app_version)

        base_sling = Sling(credentials=creds, requester=RequestsRequester()).headers({
            'User-Agent': user_agent,
        })

        rest_sling = base_sling.new().base('https://rest.nexmo.com')
        api_sling =  base_sling.new().base('https://api.nexmo.com')

        self.sms = SMSProvider(rest_sling)

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
