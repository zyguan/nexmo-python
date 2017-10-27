import nexmo
import responses
from util import *

from nexmo import sms


@responses.activate
def test_deprecated_send_message(client, dummy_data):
    stub(responses.POST, 'https://rest.nexmo.com/sms/json')

    params = {'from': 'Python', 'to': '447525856424', 'text': 'Hey!'}

    with pytest.deprecated_call():
        result = client.send_message(params)

    assert isinstance(result, dict)
    assert request_user_agent() == dummy_data.user_agent
    assert 'from=Python' in request_body()
    assert 'to=447525856424' in request_body()
    assert 'text=Hey%21' in request_body()


@responses.activate
def test_send_message(client, dummy_data):
    stub("POST", 'https://rest.nexmo.com/sms/json')
    result = client.sms.send_text(
        from_='Python',
        to='447700900693',
        text='Hey!', )
    # assert not isinstance(result, dict)
    print("Headers:", responses.calls[0].request.headers)
    assert request_user_agent() == dummy_data.user_agent
    assert 'from=Python' in request_body()
    assert 'to=447700900693' in request_body()
    assert 'text=Hey%21' in request_body()
    assert 'api_key=nexmo-api-key' in request_body()


@responses.activate
def test_thing(client: nexmo.Client):
    stub(responses.POST, 'https://rest.nexmo.com/sms/json')
    a = 12
    b = 'abc'
    client.sms.send_text(from_=a, to=b, text='abc')


@responses.activate
def test_authentication_error(client):
    responses.add(
        responses.POST, 'https://rest.nexmo.com/sms/json', status=401)

    with pytest.raises(nexmo.AuthenticationError):
        client.send_message({})


@responses.activate
def test_client_error(client):
    responses.add(
        responses.POST, 'https://rest.nexmo.com/sms/json', status=400)

    with pytest.raises(nexmo.ClientError) as excinfo:
        client.send_message({})
    excinfo.match(r'400 response from rest.nexmo.com')


@responses.activate
def test_server_error(client):
    responses.add(
        responses.POST, 'https://rest.nexmo.com/sms/json', status=500)

    with pytest.raises(nexmo.ServerError) as excinfo:
        client.send_message({})
    excinfo.match(r'500 response from rest.nexmo.com')


def test_deserialise_send_message_response():
    ser = """
    {
    "message-count": "1",
    "messages": [
        {
        "to": "447700900526",
        "message-id": "0B0000008F7CEFF7",
        "status": "0",
        "remaining-balance": "37.36096950",
        "message-price": "0.03330000",
        "network": "23410"
        }
    ]
    } """
    loaded = sms.SendMessageResponseSchema().load(ser)
    assert loaded.message_count == 1
