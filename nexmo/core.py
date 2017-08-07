from platform import python_version


class Config(object):
    def __init__(self, credentials, nexmo_version, app_name=None, app_version=None):
        user_agent = 'nexmo-python/{0}/{1}'.format(nexmo_version, python_version())
        if app_name is not None and 'app_version' is not None:
            user_agent += '/{0}/{1}'.format(app_name, app_version)

        self.user_agent = user_agent
        self.headers = {'User-Agent': user_agent}
        self.credentials = credentials
