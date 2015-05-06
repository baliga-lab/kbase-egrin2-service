import requests


class AWEClient:
    """A convenience class to access an AWE service
    """
    def __init__(self, base_url, auth_token):
        self.base_url = base_url
        self.auth_token = auth_token

    def auth_headers(self):
        return {'Authorization': 'OAuth %s' % self.auth_token}

    def submit_job(self, path):
        files = {'upload': open(path)}
        r = requests.post(self.base_url + '/job', files=files,
                          headers=self.auth_headers())
        return r.json()