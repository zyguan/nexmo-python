

class AuthenticationError(Exception): pass


class AuthCollection(object):
    def __init__(self):
        self.auth_providers = []

    def append(self, auth_provider):
        self.auth_providers.append(auth_provider)

    def __iter__(self):
        return iter(self.auth_providers)


class AuthProvider(object):
    pass


class SecretAuthProvider(object):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret


class SignatureAuthProvider(object):
    def __init__(self, api_key, signature_secret):
        self.api_key = api_key
        self.signature_secret = signature_secret


class JWTAuthProvider(object):
    def __init__(self, application_id, private_key):
        self.application_id = application_id
        self.private_key = private_key


def requires_auth(supported):
    def requires_auth_decorator(target):
        def requires_auth_wrapper(self, *args, **kwargs):
            return target(self, *args, **kwargs)
        return requires_auth_wrapper
    return requires_auth_decorator