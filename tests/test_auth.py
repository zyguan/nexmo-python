import conftest
import pytest
from unittest import mock
from nexmo.auth import *

import requests
from nexmo.core import Sling


def test_empty_auth():
    collection = CredentialsCollection()

    with pytest.raises(AuthenticationError) as ae:
        collection.create_auth((SecretParamsAuth, SecretBodyAuth,
                                SignatureAuth, JWTAuth, ))
    assert str(ae.value) == (
        "Missing authentication. You must provide one or more of:\n" +
        "   application_id and private_key\n" + "   api_key and api_secret\n" +
        "   api_key and signature_secret")


def test_auth():
    collection = CredentialsCollection()
    pkc = PrivateKeyCredentials("dummy_application_id", "dummy_private_key")
    sc = SecretCredentials("dummy_api_key", "dummy_api_secret")
    sig_c = SignatureCredentials("dummy_api_key", "dummy_secret")
    collection.append(sc)
    collection.append(pkc)
    collection.append(sig_c)

    auth = collection.create_auth((JWTAuth, ))
    assert auth.credentials is pkc

    auth = collection.create_auth((SecretParamsAuth, ))
    assert auth.credentials is sc

    auth = collection.create_auth((SecretBodyAuth, ))
    assert auth.credentials is sc

    auth = collection.create_auth((SignatureAuth, ))
    assert auth.credentials is sig_c


def test_AuthProvider_call_fails():
    with pytest.raises(NotImplementedError):
        AuthProvider(credentials=None)(None)


def test_SecretParamsAuth():
    request = mock.MagicMock(spec=["params"])
    SecretParamsAuth(
        SecretCredentials("dummy_api_key", "dummy_api_secret"))(request)
    request.params.assert_called_once_with(dict(
        api_key="dummy_api_key",
        api_secret="dummy_api_secret",
    ))


def test_SecretBodyAuth():
    request = mock.MagicMock(spec=["params"])
    SecretBodyAuth(
        SecretCredentials("dummy_api_key", "dummy_api_secret"))(request)
    request.params.assert_called_once_with(dict(
        api_key="dummy_api_key",
        api_secret="dummy_api_secret",
    ))


def test_JWTAuth():
    request = Sling() # mock.MagicMock(spec=["headers"])

    #  mock.patch("time.time", return_value=1000),\
    with mock.patch("uuid.uuid4", return_value="872d8060-fdf5-4bd1-a583-1ce4463e5544"):
        auth = JWTAuth(
            PrivateKeyCredentials("dummy_application_id",
                                  conftest.read_file("data/private_key.txt")))(
                                      request)
        import jwt
        data = jwt.decode(request._headers['Authorization'][7:], conftest.read_file("data/public_key.txt"), algorithms=['RS256'])
        assert data['application_id'] == 'dummy_application_id'


def test_SignatureAuth():
    request = Sling().base('https://rest.nexmo.com/sms/json').params({
        "from": "447700900708",
        "to": "447700900709",
        "text": "Hello Nexmo!",
    }).post()

    with mock.patch.object(
            SignatureAuth, '_time', return_value=1507640281.326199):
        auth = SignatureAuth(credentials=SignatureCredentials(
            'dummy-api-key', 'not-a-secret'))
        auth(request)
        assert request._params.get('api_key') == 'dummy-api-key'
        assert request._params.get('sig') == '682cb6d85d6fe805302e195708871394'
