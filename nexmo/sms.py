'''
nexmo.sms - Nexmo SMS API interface.
'''

from .auth import requires_auth, SecretBodyAuth, SignatureAuth
from .exceptions import AuthenticationError, ClientError, ServerError

import attr
from marshmallow import Schema, fields, post_load


class MessagePartSchema(Schema):
    to = fields.Str()
    message_id = fields.Str(load_from="message-id")
    status = fields.Int()
    remaining_balance = fields.Decimal(load_from="remaining-balance")
    message_price = fields.Decimal(load_from="message-price")
    network = fields.Str()

    @post_load
    def make_object(self, data):
        return MessagePart(**data)


class SendMessageResponseSchema(Schema):
    message_count = fields.Str()
    messages = MessagePartSchema(many=True)

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


class BaseSMSProvider:
    def __init__(self, sling):
        self._sling = sling.new().path('sms')

    def _send_text_sling(
            self,
            *,
            from_,
            to,
            text,
            unicode_=False,
            status_report_req=False,
            callback=None,
            message_class=None,
    ):
        sling = self._sling.new() \
            .post('json') \
            .auth([SignatureAuth, SecretBodyAuth]) \
            .params({
                'from': from_,
                'to': to,
                'text': text,
                'type': 'text' if not unicode_ else 'unicode',
            })
        if status_report_req or callback is not None:
            sling.params({'status-report-req': 1})
        if callback is not None:
            sling.params({'callback': callback})
        if message_class is not None:
            sling.params({'message-class': message_class})
        return sling


class AsyncSMSProvider(BaseSMSProvider):
    async def send_text(
            self,
            *,
            from_,
            to,
            text,
            unicode_=False,
            status_report_req=False,
            callback=None,
            message_class=None,
    ):
        """
        Send an SMS text or unicode message.

        :param str from_:
        :param str to:
        :param str text:
        :param bool unicode_:
        :param bool status_report_req:
        :param str callback:
        :param int message_class:
        :return:
        """

        sling = self._send_text_sling(
            from_=from_,
            to=to,
            text=text,
            unicode_=unicode_,
            status_report_req=status_report_req,
            callback=callback,
            message_class=message_class,
        )
        return parse_response(await sling.do_async())


class SMSProvider(BaseSMSProvider):
    def __init__(self, sling):
        self._sling = sling.new().path('sms')

    def send_text(
            self,
            *,
            from_,
            to,
            text,
            unicode_=False,
            status_report_req=False,
            callback=None,
            message_class=None,
    ):
        """
        Send an SMS text or unicode message.

        :param str from_:
        :param str to:
        :param str text:
        :param bool unicode_:
        :param bool status_report_req:
        :param str callback:
        :param int message_class:
        :return:
        """

        sling = self._send_text_sling(
            from_=from_,
            to=to,
            text=text,
            unicode_=unicode_,
            status_report_req=status_report_req,
            callback=callback,
            message_class=message_class,
        )
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
        message = "{code} response from server".format(
            code=response.status_code)
        raise ClientError(message)
    elif 500 <= response.status_code < 600:
        message = "{code} response from server".format(
            code=response.status_code)
        raise ServerError(message)
