import json

import nexmo
import responses
from util import *

from nexmo import sms

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
    loaded = sms.SendMessageResponseSchema().load(json.loads(ser))
    assert loaded.message_count == 1
