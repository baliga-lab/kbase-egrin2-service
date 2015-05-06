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


class Command:
    def __init__(self, name, args='', description=''):
        self.cmd = {'name': name, 'args': args, 'description': description}


class WorkflowDocumentBuilder:
    """a builder class to help creating an AWE workflow document"""

    def __init__(self, pipeline, name, project, user, clientgroups, tasks=[], noretry=True):
        self.doc = {
            'info': { 'pipeline': pipeline, 'name': name, 'project': project,
                      'user': user, 'clientgroups': clientgroups, 'noretry': noretry
                  },
            'tasks': tasks
        }

    def add_task(self, command, task_id, skip=False, totalwork=1, depends_on=[]):
        skip_num = 1 if skip else 0

        self.doc['tasks'].append({
            'cmd': command.cmd,
            'taskid': task_id,
            'skip': skip_num,
            'dependsOn': depends_on
        })
