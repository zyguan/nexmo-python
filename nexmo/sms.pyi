import sys


class SMSProvider(object):
    def send_text(
        self,
        from_: str,
        to: str,
        text: str,
        unicode_: bool=False,
        status_report_req: bool=False,
        callback: str=None,
        message_class:int=None,
    ) -> dict:
        ...
