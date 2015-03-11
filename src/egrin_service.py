#!/usr/bin/env python
from flask import Flask, Response
import flask
import json

import biokbase.auth as auth

app = Flask(__name__)

@app.route('/')
def index():
    content = {'msg': 'Hello world'}
    return Response(json.dumps(content), mimetype='application/json')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
