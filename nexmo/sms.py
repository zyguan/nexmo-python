import requests
import sys

from .provider import Provider, requires_auth

if sys.version_info[0] == 3:
    string_types = (str, bytes)
else:
    string_types = (unicode, str)


class SMSProvider(Provider):
    def __init__(self, auth):
        pass

    @requires_auth(supported=[])
    def send_text(
        self,
        from_,
        to,
        text,
        unicode=False,
        status_report_req=False,
        callback=None,
        message_class=None,
        **kwargs
    ):
        """
        Send an SMS message.
        
        :param string_types from_: 
        :param string_types to: 
        :param string_types text: 
        :param bool unicode:
        :param  status_report_req: 
        :param callback: 
        :param message_class: 
        :return: 
        """
        params = {
            'from': from_,
            'to': to,
            'text': text,
            'type': 'text' if not unicode else 'unicode',
        }

        if status_report_req or callback is not None:
            params['status-report-req'] = 1

        if callback is not None:
            params['callback'] = callback

        if message_class is not None:
            params['message-class'] = message_class

        uri = 'https://' + self.host + '/sms/json'

        params.update(api_key=self.api_key, api_secret=self.api_secret)

        response = requests.post(uri, data=params, headers=self.headers)

        if response.status_code == 401:
            raise AuthenticationError()
        elif response.status_code == 204:
            return None
        elif 200 <= response.status_code < 300:
            return response.json()
        elif 400 <= response.status_code < 500:
            message = "{code} response from {host}".format(code=response.status_code, host=self.host)
            raise ClientError(message)
        elif 500 <= response.status_code < 600:
            message = "{code} response from {host}".format(code=response.status_code, host=self.host)
            raise ServerError(message)

        self.parse(host, )
