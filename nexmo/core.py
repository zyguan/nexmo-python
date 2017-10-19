from platform import python_version

from urllib.parse import urljoin


class IllegalStateError(Exception):
    pass


class Config:
    def __init__(self,
                 credentials,
                 nexmo_version,
                 app_name=None,
                 app_version=None):
        user_agent = 'nexmo-python/{0}/{1}'.format(nexmo_version,
                                                   python_version())
        if app_name is not None and 'app_version' is not None:
            user_agent += '/{0}/{1}'.format(app_name, app_version)

        self.user_agent = user_agent
        self.headers = {'User-Agent': user_agent}
        self.credentials = credentials


class Sling:
    def __init__(self, *, url=None, method=None, headers=None, params=None):
        self._method = method or "GET"
        self._headers = headers or {}
        self._params = params or {}
        self._raw_url = url or None

    def new(self):
        return self.__class__(
            url=self._raw_url,
            method=self._method,
            headers=dict(self._headers),
            params=dict(self._params))

    def base(self, value):
        self._raw_url = value
        return self

    def path(self, path):
        self._raw_url = urljoin(self._raw_url, path)
        return self

    def params(self, params):
        self._params.update(params)
        return self

    def headers(self, headers):
        self._headers.update(headers)
        return self

    def method(self, method):
        self._method = method
        return self

    def get(self, path=None):
        return self.method("GET").path(path)

    def put(self, path=None):
        return self.method("PUT").path(path)

    def post(self, path=None):
        return self.method("POST").path(path)

    def delete(self, path=None):
        return self.method("DELETE").path(path)
