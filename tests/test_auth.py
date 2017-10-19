import conftest
import pytest
from unittest import mock
from nexmo.auth import *

import requests


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
    request.params.update.assert_called_once_with(
        api_key="dummy_api_key",
        api_secret="dummy_api_secret", )


def test_SecretBodyAuth():
    request = mock.MagicMock(spec=["data"])
    SecretBodyAuth(
        SecretCredentials("dummy_api_key", "dummy_api_secret"))(request)
    request.data.update.assert_called_once_with(
        api_key="dummy_api_key",
        api_secret="dummy_api_secret", )


def test_JWTAuth():
    request = mock.MagicMock(spec=["headers"])

    with mock.patch("time.time", return_value=1000),\
        mock.patch("uuid.uuid4", return_value="872d8060-fdf5-4bd1-a583-1ce4463e5544"):
        auth = JWTAuth(
            PrivateKeyCredentials("dummy_application_id",
                                  conftest.read_file("data/private_key.txt")))(
                                      request)
        request.headers.__setitem__.assert_called_with(
            'Authorization',
            b'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhcHBsaWNhdGlvbl9pZCI6ImR1bW15X2FwcGxpY2F0aW9uX2lkIiwiaWF0IjoxMDAwLCJleHAiOjEwNjAsImp0aSI6Ijg3MmQ4MDYwLWZkZjUtNGJkMS1hNTgzLTFjZTQ0NjNlNTU0NCJ9.SxUnnRKItAJktVktF_P2-dvckxswr955sHBbKqvwxTXkD4wAfUv5P5qPD1tI7iGk0udDlJ30CdvTA8vHG26TSoK_f_7qayPQWSOqKG060bJEBGdBkTjlh4ogLJTGbd25L1m1QHGq5x---17SjejoZm27D2noEzQD7uKaL74Y0keN-6C1DrqHnTnvvIKei3tsEQ7JXNWFuV28S06LN-r221j20dLbQ16drwM1MFD8ICGENEWud5enjBYxOtg6xPwosz7aRVC0ZIaclw6QNBxADuYe0Hy8ndj6889Pi5GmiejESnIpSY0BBVFKAMmf5IR12nXFI3UekgFvqFbU3dW4Aw'
        )


def test_SignatureAuth():
    request = requests.Request(
        'POST',
        "https://rest.nexmo.com/sms/json",
        data={
            "from": "447700900708",
            "to": "447700900709",
            "text": "Hello Nexmo!",
        })

    with mock.patch.object(
            SignatureAuth, '_time', return_value=1507640281.326199):
        auth = SignatureAuth(credentials=SignatureCredentials(
            'dummy-api-key', 'not-a-secret'))
        auth(request)
        assert request.data.get('api_key') == 'dummy-api-key'
        assert request.data.get('sig') == '682cb6d85d6fe805302e195708871394'
