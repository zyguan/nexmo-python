import functools
import hashlib
import time
# TODO: Make py2 compatible
from urllib.parse import encode as encode_params
from .exceptions import AuthenticationError


class SecretCredentials(object):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def description(self):
        "api_key and api_secret"


class SignatureCredentials(object):
    def __init__(self, api_key, signature_secret):
        self.api_key = api_key
        self.signature_secret = signature_secret

    def description(self):
        "api_key and signature_secret"


class PrivateKeyCredentials(object):
    def __init__(self, application_id, private_key):
        self.application_id = application_id
        self.private_key = private_key

    def description(self):
        "application_id and private_key"


class CredentialsCollection(object):
    def __init__(self):
        self.credentials = []

    def append(self, credentials):
        self.credentials.append(credentials)

    def _of_type(self, t):
        for creds in self.credentials:
            if isinstance(creds, t):
                return creds
        return None

    def create_auth(self, auth_options):
        missing_creds = []
        for auth in auth_options:
            creds = self._of_type(auth.credentials_type)
            if creds:
                return auth(creds)
            else:
                missing_creds.append(auth.description())
        raise AuthenticationError(
            "Missing authentication. You must provide one or more of:"
            + '\n'.join('   ' + m for m in missing_creds))


    def __iter__(self):
        return iter(self.credentials)


class AuthProvider(object):
    credentials_type = None

    def __init__(self, credentials):
        self.credentials = credentials
    
    def __call__(self, request):
        raise NotImplementedError("AuthProviders must implement __call__")


class SecretParamsAuth(AuthProvider):
    credentials_type = SecretCredentials

    def __call__(self, request):
        request.params.extend(
            api_key=self.credentials.api_key,
            api_secret=self.credentials.api_secret,
        )


class SecretBodyAuth(AuthProvider):
    credentials_type = SecretCredentials

    def __call__(self, request):
        request.body.extend(
            api_key=self.credentials.api_key,
            api_secret=self.credentials.api_secret,
        )


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
        request.params.extend(
            api_key=self.credentials.api_key,
            timestamp=int(self._time()),
        )
        request.params.extend(
            sig=self._signature(request.params),
        )


class JWTAuth(AuthProvider):
    credentials_type = PrivateKeyCredentials

    # TODO: Must implement __call__


def requires_auth(supported):
    def requires_auth_decorator(target):
        @functools.wraps(target)
        def requires_auth_wrapper(self, *args, **kwargs):
            auth = self._credentials.create_auth(supported)
            return target(self, *args, _auth=auth, **kwargs)
        return requires_auth_wrapper
    return requires_auth_decorator
