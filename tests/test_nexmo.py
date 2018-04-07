try:
    from urllib.parse import urlparse, quote_plus
except ImportError:
    from urlparse import urlparse
    from urllib import quote_plus

import nexmo
from util import *

def test_check_signature(dummy_data):
    params = {
        'a': '1',
        'b': '2',
        'timestamp': '1461605396',
        'sig': '6af838ef94998832dbfc29020b564830'
    }

    client = nexmo.Client(
        key=dummy_data.api_key,
        secret=dummy_data.api_secret,
        signature_secret='secret')

    assert client.check_signature(params)


def test_signature(client, dummy_data):
    params = {'a': '1', 'b': '2', 'timestamp': '1461605396'}
    client = nexmo.Client(
        key=dummy_data.api_key,
        secret=dummy_data.api_secret,
        signature_secret='secret')
    assert client.signature(params) == '6af838ef94998832dbfc29020b564830'


def test_client_doesnt_require_api_key():
    client = nexmo.Client(application_id='myid', private_key='abc\nde')
    assert client is not None
    assert client.api_key is None
    assert client.api_secret is None
