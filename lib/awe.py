import requests
import json


class AWEClient:
    """A convenience class to access an AWE service
    """
    def __init__(self, base_url, auth_token):
        self.base_url = base_url
        self.auth_token = auth_token

    def auth_headers(self):
        """set the authorization token needed to access Shock"""
        return {'Datatoken': '%s' % self.auth_token}

    def submit_job(self, path):
        files = {'upload': open(path)}
        r = requests.post(self.base_url + '/job', files=files,
                          headers=self.auth_headers())
        return r.json


class Command:
    def __init__(self, name, args='', description=''):
        self.cmd = {'name': name, 'args': args, 'description': description}


class Task:
    def __init__(self, command, task_id, totalwork=1, depends_on=[], skip=False,
                 inputs={}, outputs={}):
        skip_num = 1 if skip else 0
        self.task = {'cmd': command.cmd,
                     'taskid': task_id,
                     'skip': skip_num,
                     'dependsOn': depends_on,
                     'inputs': inputs,
                     'outputs': outputs
                 }

    def add_shock_input(self, refname, url, node):
        self.task['inputs'][refname] = {'host': url, 'node': node }

    def add_shock_output(self, refname, url, attrfile):
        self.task['outputs'][refname] = {'host': url, 'attrfile': attrfile}


class WorkflowDocumentBuilder:
    """a builder class to help creating an AWE workflow document"""

    def __init__(self, pipeline, name, project, user, clientgroups, tasks=[],
                 noretry=True, auth=True):
        self.doc = {
            'info': { 'pipeline': pipeline, 'name': name, 'project': project,
                      'user': user, 'clientgroups': clientgroups, 'noretry': noretry
                  },
            'tasks': tasks
        }

    def add_task(self, task):
        self.doc['tasks'].append(task.task)

if __name__ == '__main__':
    builder = WorkflowDocumentBuilder('pipeline1', 'name1', 'prj1', 'user1', 'group1')
    command = Command('mycmd', 'args')
    task = Task(command, 1)
    task.add_shock_input('mafile', 'http://shocky.com', 'node1')
    builder.add_task(task)
    print json.dumps(builder.doc)
