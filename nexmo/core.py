#!python3

import logging
from platform import python_version
from urllib.parse import urljoin
from textwrap import dedent

import aiohttp
import requests

from .auth import CredentialsCollection

__all__ = [
    "IllegalStateError",
    "Sling",
]

LOG = logging.getLogger('nexmo.core')


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
    def __init__(self, *, auth=None, credentials=None, headers=None, method=None, params=None, requester=None,
                 url=None):
        self._auth = auth
        self._credentials = credentials if credentials is not None else CredentialsCollection()
        self._requester = requester

        self._method = method or "GET"
        self._headers = headers or {}
        self._params = params or {}
        self._url = url or None

    def new(self):
        return self.__class__(
            auth=self._auth,
            credentials=self._credentials,
            requester=self._requester,
            url=self._url,
            method=self._method,
            headers=dict(self._headers),
            params=dict(self._params))

    def base(self, value):
        self._url = value
        return self

    def path(self, path):
        LOG.debug("Setting path (%r) with %r", self._url, path)
        self._url = urljoin(self._url, path)
        LOG.debug("Resulting url: %r", self._url)

        return self

    def auth(self, supported):
        self._auth = self._credentials.create_auth(supported)
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

    def __repr__(self):
        return dedent('''
        <{self.__class__.__name__}(
            auth={self._auth!r},
            credentials={self._credentials!r},
            requester={self._requester!r},
            url={self._url!r},
            method={self._method!r},
            headers={self._headers!r},
            params={self._params!r},
        )>'''.format(self=self)).strip()

    def _apply_auth(self):
        if self._auth is not None:
            sling = self.new()
            sling._auth(self)
            return sling
        return self

    async def do_async(self):
        return await self._apply_auth()._requester.request(self)

    def do(self):
        return self._apply_auth()._requester.request(self)


class AioHttpRequester:
    def __init__(self):
        self._session = aiohttp.ClientSession()

    def close(self):
        if self._session is not None:
            self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.close()

    async def request(self, sling):
        return await self._session.request(
            method=sling._method,
            url=sling._url,
            params=sling._params if sling._method not in {'POST', 'PUT'} else None,
            data=sling._params if sling._method in {'POST', 'PUT'} else None,
        )

    def __repr__(self):
        return '<{self.__class__.__name__} {id:X}>'.format(self=self, id=id(self))


class RequestsRequester:
    def __init__(self):
        self._session = requests.Session()

    def close(self):
        if self._session is not None:
            self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.close()

    def request(self, sling):
        return self._session.request(
            headers=sling._headers,
            method=sling._method,
            url=sling._url,
            params=sling._params if sling._method not in {'POST', 'PUT'} else None,
            data=sling._params if sling._method in {'POST', 'PUT'} else None,
        )

    def __repr__(self):
        return '<{self.__class__.__name__} {id:X}>'.format(self=self, id=id(self))
