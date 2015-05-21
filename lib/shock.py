import requests


class ShockClient:
    """A convenience class to access a Shock service
    It handles the aspects:

    - Authentication
    - Upload
    - Download
    """
    def __init__(self, base_url, auth_token):
        self.base_url = base_url
        self.auth_token = auth_token

    def auth_headers(self):
        return {'Authorization': 'OAuth %s' % self.auth_token}

    def upload_file(self, path):
        files = {'upload': open(path)}
        r = requests.post(self.base_url + '/node', files=files,
                          headers=self.auth_headers())
        return r.json

    def node_info(self, node_id):
        r = requests.get(self.base_url + '/node/%s' % node_id,
                         headers=self.auth_headers())
        return r.json

    def download_file(self, node_id, target_path):
        r = requests.get(self.base_url + '/node/%s?download_raw' % node_id,
                         headers=self.auth_headers(), stream=True)
        with open(target_path, 'wb') as outfile:
            for chunk in r.iter_content(256):
                outfile.write(chunk)
