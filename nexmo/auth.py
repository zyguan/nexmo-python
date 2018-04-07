from collections import abc
import functools
import hashlib
from operator import attrgetter
import time
import logging
import uuid
import jwt

from .exceptions import AuthenticationError

LOG = logging.getLogger('nexmo.auth')


class SecretCredentials:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    @staticmethod
    def description():
        return "api_key and api_secret"


class SignatureCredentials:
    def __init__(self, api_key, signature_secret):
        self.api_key = api_key
        self.signature_secret = signature_secret

    @staticmethod
    def description():
        return "api_key and signature_secret"


class PrivateKeyCredentials:
    def __init__(self, application_id, private_key):
        self.application_id = application_id
        self.private_key = private_key

    @staticmethod
    def description():
        return "application_id and private_key"


class CredentialsCollection:
    def __init__(self, credentials=None):
        if credentials is None:
            self._credentials = []
        elif isinstance(credentials, abc.Sequence):
            self._credentials = list(credentials)
        else:
            self._credentials = [credentials]

    def append(self, credentials):
        self._credentials.append(credentials)

    def _of_type(self, t):
        # It would be easy to store a dict of { credentials-type -> credentials-instance }, but we need to
        # also deal with subclasses, so:
        for creds in self:
            if isinstance(creds, t):
                return creds
        return None

    def create_auth(self, auth_options):
        LOG.debug("Configured credentials: %r", self._credentials)
        missing_creds = set()
        for auth in auth_options:
            creds = self._of_type(auth.credentials_type)
            LOG.debug("Looking for creds of type %s", auth.credentials_type.__name__)
            LOG.debug("Found: %r", creds)
            if creds:
                return auth(creds)
            else:
                missing_creds.add(auth.credentials_type)
        raise AuthenticationError(
            "Missing authentication. You must provide one or more of:\n" +
            '\n'.join(
                '   ' + m.description()
                for m in sorted(missing_creds, key=attrgetter("__name__"))))

    def __iter__(self):
        return iter(self._credentials)


class AuthProvider:
    credentials_type = None

    def __init__(self, credentials):
        self.credentials = credentials

    def __call__(self, sling):
        raise NotImplementedError("AuthProviders must implement __call__")


class SecretParamsAuth(AuthProvider):
    credentials_type = SecretCredentials

    def __call__(self, sling):
        LOG.warning("Secret params authentication")
        sling.params(dict(
            api_key=self.credentials.api_key,
            api_secret=self.credentials.api_secret, ))


class SecretBodyAuth(AuthProvider):
    credentials_type = SecretCredentials

    def __call__(self, sling):
        LOG.warning("Secret body authentication")
        sling.params(dict(
            api_key=self.credentials.api_key,
            api_secret=self.credentials.api_secret, ))


class SignatureAuth(AuthProvider):
    credentials_type = SignatureCredentials

    def _signature(self, params):
        md5 = hashlib.md5()
        param_string = _encode_params(sorted(params.items()))
        plaintext = '&' + param_string + self.credentials.signature_secret
        md5.update(plaintext.encode())
        return md5.hexdigest()

    def _time(self):
        return time.time()

    def _modify_params(self, sling):
        sling.params(
            dict(
                api_key=self.credentials.api_key,
                timestamp=int(self._time()), ))
        sling.params(dict(
            sig=self._signature(sling._params), ))

    def __call__(self, request):
        LOG.warning("Signature authentication")
        self._modify_params(request.data)


class JWTAuth(AuthProvider):
    credentials_type = PrivateKeyCredentials

    def __call__(self, sling):
        iat = int(time.time())

        # TODO: Think about auth_params
        payload = {}  # dict(self.auth_params)
        payload.setdefault('application_id', self.credentials.application_id)
        payload.setdefault('iat', iat)
        payload.setdefault('exp', iat + 60)
        payload.setdefault('jti', str(uuid.uuid4()))

        token = jwt.encode(
            payload, self.credentials.private_key, algorithm='RS256')

        sling.headers({'Authorization', b'Bearer ' + token})


# FIXME: Probably not going to use this.
def requires_auth(supported):
    def requires_auth_decorator(target):
        @functools.wraps(target)
        def requires_auth_wrapper(self, *args, **kwargs):
            auth = self.config.credentials.create_auth(supported)
            return target(self, *args, _auth=auth, **kwargs)

        return requires_auth_wrapper

    return requires_auth_decorator


def _encode_params(params):
    return '&'.join('{q}={v}'.format(q=k, v=v) for k, v in params)
