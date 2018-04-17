"""
nexmo.sms - Nexmo SMS API interface.
"""

from .auth import SecretBodyAuth, SignatureAuth
from .exceptions import AuthenticationError, ClientError, ServerError

import attr
from marshmallow import Schema, fields, post_load


@attr.s
class TextSMSMessage:
    """ An SMS text or unicode message. """
    from_ = attr.ib(type=str)
    to = attr.ib(type=str)
    text = attr.ib(type=str)
    unicode_ = attr.ib(default=False, type=bool)
    status_report_req = attr.ib(default=False, type=bool)
    callback = attr.ib(default=None, type=str)
    message_class = attr.ib(
        default=None, type=int
    )  # Left this as an int, not an enum. Range 0-3
    ttl = attr.ib(default=None, type=int)
    client_ref = attr.ib(default=None, type=str)

    @message_class.validator
    def message_class_in_range(self, _attribute, value):
        if value is not None and not 0 <= value <= 3:
            raise ValueError("message_class must be in the range 0-3 inclusive.")

    def apply_to_sling(self, sling):
        (
            sling.post("json").auth([SignatureAuth, SecretBodyAuth]).params(
                {
                    "from": self.from_,
                    "to": self.to,
                    "text": self.text,
                    "type": "text" if not self.unicode_ else "unicode",
                }
            )
        )
        if self.status_report_req or self.callback is not None:
            sling.params({"status-report-req": 1})
        if self.callback is not None:
            sling.params({"callback": self.callback})
        if self.message_class is not None:
            sling.params({"message-class": self.message_class})
        if self.ttl is not None:
            sling.params({"ttl": self.ttl})
        if self.client_ref is not None:
            sling.params({"client-ref": self.client_ref})
        return sling


class MessagePartSchema(Schema):
    to = fields.Str()
    message_id = fields.Str(data_key="message-id")
    status = fields.Int()
    remaining_balance = fields.Decimal(data_key="remaining-balance")
    message_price = fields.Decimal(data_key="message-price")
    network = fields.Str()

    @post_load
    def make_object(self, data):
        print(data)
        return MessagePart(**data)


class SendMessageResponseSchema(Schema):
    message_count = fields.Int(data_key="message-count")
    messages = fields.Nested(MessagePartSchema, many=True)

    @post_load
    def make_object(self, data):
        return SendMessageResponse(**data)


@attr.s
class SendMessageResponse:
    message_count = attr.ib()
    messages = attr.ib()


@attr.s
class MessagePart:
    to = attr.ib()
    message_id = attr.ib()
    status = attr.ib()
    remaining_balance = attr.ib()
    message_price = attr.ib()
    network = attr.ib()


class AsyncSMSProvider:

    def __init__(self, sling):
        self._sling = sling.new().path("sms/")

    async def send_sms(self, sms_message: TextSMSMessage):
        """
        Send an SMS text or unicode message.
        :return:
        """

        sling = sms_message.apply_to_sling(self._sling.new())
        return parse_response(await sling.do_async())


class SMSProvider:

    def __init__(self, sling):
        self._sling = sling.new().path("sms/")

    def send_sms(self, sms_message: TextSMSMessage):
        """
        Send an SMS text or unicode message.
        :return:
        """

        sling = sms_message.apply_to_sling(self._sling.new())
        return parse_response(sling.do())


def parse_response(response, response_type=None):
    if response.status_code == 401:
        raise AuthenticationError()

    elif response.status_code == 204:
        return None

    elif 200 <= response.status_code < 300:
        json = response.json()
        if response_type is None:
            return json

        else:
            # TODO: Handle object mapping here:
            return json

    elif 400 <= response.status_code < 500:
        message = "{code} response from server".format(code=response.status_code)
        raise ClientError(message)

    elif 500 <= response.status_code < 600:
        message = "{code} response from server".format(code=response.status_code)
        raise ServerError(message)
