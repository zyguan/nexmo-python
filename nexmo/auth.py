import functools
import hashlib
import time
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus
from .exceptions import AuthenticationError
import logging
import uuid

import jwt

log = logging.getLogger('nexmo.auth')

class SecretCredentials(object):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    @staticmethod
    def description(self):
        return "api_key and api_secret"


class SignatureCredentials(object):
    def __init__(self, api_key, signature_secret):
        self.api_key = api_key
        self.signature_secret = signature_secret

    @staticmethod
    def description(self):
        return "api_key and signature_secret"


class PrivateKeyCredentials(object):
    def __init__(self, application_id, private_key):
        self.application_id = application_id
        self.private_key = private_key

    @staticmethod
    def description(self):
        return "application_id and private_key"


class CredentialsCollection(object):
    def __init__(self):
        self._credentials = []

    def append(self, credentials):
        self._credentials.append(credentials)

    def _of_type(self, t):
        for creds in self._credentials:
            if isinstance(creds, t):
                return creds
        return None

    def create_auth(self, auth_options):
        missing_creds = set()
        for auth in auth_options:
            creds = self._of_type(auth.credentials_type)
            if creds:
                return auth(creds)
            else:
                missing_creds.add(auth.credentials_type)
        raise AuthenticationError(
            "Missing authentication. You must provide one or more of:"
            + '\n'.join('   ' + m.description() for m in sorted(missing_creds)))

    def __iter__(self):
        return iter(self._credentials)


class AuthProvider(object):
    credentials_type = None

    def __init__(self, credentials):
        self.credentials = credentials
    
    def __call__(self, request):
        raise NotImplementedError("AuthProviders must implement __call__")


class SecretParamsAuth(AuthProvider):
    credentials_type = SecretCredentials

    def __call__(self, request):
        log.warning("Secret params authentication")
        request.params.update(
            api_key=self.credentials.api_key,
            api_secret=self.credentials.api_secret,
        )


class SecretBodyAuth(AuthProvider):
    credentials_type = SecretCredentials

    def __call__(self, request):
        log.warning("Secret body authentication")
        print(request.data)
        request.data.update(dict(
            api_key=self.credentials.api_key,
            api_secret=self.credentials.api_secret,
        ))
        print(request.data)


class SignatureAuth(AuthProvider):
    credentials_type = SignatureCredentials

    def _signature(self, params):
        md5 = hashlib.md5()
        param_string = encode_params(sorted(params))
        md5.update(param_string)
        md5.update(self.credentials.signature_secret.encode('utf-8'))
        return md5.digest()

    def _time(self):
        time.time()

    def __call__(self, request):
        log.warning("Signature authentication")
        request.params.extend(dict(
            api_key=self.credentials.api_key,
            timestamp=int(self._time()),
        ))
        request.params.extend(
            sig=self._signature(request.params),
        )


class JWTAuth(AuthProvider):
    credentials_type = PrivateKeyCredentials

    def __call__(self, request):
        iat = int(time.time())

        payload = dict(self.auth_params)
        payload.setdefault('application_id', self.credentials.application_id)
        payload.setdefault('iat', iat)
        payload.setdefault('exp', iat + 60)
        payload.setdefault('jti', str(uuid.uuid4()))

        token = jwt.encode(payload, self.credentials.private_key, algorithm='RS256')

        request.headers['Authorization'] = b'Bearer ' + token


def requires_auth(supported):
    def requires_auth_decorator(target):
        @functools.wraps(target)
        def requires_auth_wrapper(self, *args, **kwargs):
            auth = self.config.credentials.create_auth(supported)
            return target(self, *args, _auth=auth, **kwargs)
        return requires_auth_wrapper
    return requires_auth_decorator


def encode_params(params):
    return '&'.join('{q}={v}'.format(k=quote_plus(k), v=quote_plus(v)) for k, v in params)
