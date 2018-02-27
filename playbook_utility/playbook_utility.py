#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
try:
    from StringIO import StringIO as ZipIO
except:
    from io import BytesIO as ZipIO
import zipfile
import tempfile

from flask import flash, Flask, render_template, redirect, request, url_for
import requests

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='(%',
        block_end_string='%)',
        variable_start_string='((',
        variable_end_string='))',
        comment_start_string='(#',
        comment_end_string='#)',
    ))

app = CustomFlask(__name__)
app.secret_key = 'abc'

playbook_data = list()

def _prepare_playbook_data():
    """Create a data structure with all of the publicly available playbooks."""
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        response = requests.get('https://github.com/ThreatConnect-Inc/threatconnect-playbooks/archive/master.zip')
        with zipfile.ZipFile(ZipIO(response.content)) as pb_zip:
            pb_zip.extractall(tmp_dir_name)
            for path, dirs, files in os.walk(os.path.join(tmp_dir_name, 'threatconnect-playbooks-master/playbooks')):
                this_pb_data = dict()
                for file_ in files:
                    if file_.lower() == 'readme.md':
                        with open(os.path.join(path, file_)) as f:
                            this_pb_data['readme'] = f.read()
                    elif file_.lower().endswith('.pbx'):
                        with open(os.path.join(path, file_)) as f:
                            pb_json = json.load(f)
                            this_pb_data['name'] = pb_json['name']
                            this_pb_data['description'] = pb_json['description']

                if this_pb_data != {}:
                    playbook_data.append(this_pb_data)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/requester")
def requester_index():
    return render_template("requester_index.html")


@app.route("/requester/json")
def parse_json():
    if request.args.get('url'):
        r = requests.get(request.args['url'])

        if r.ok:
            return render_template("json.html", responseData=r.text, url=request.args['url'])
        else:
            flash('Got a {} response code from {}. Please try another site or copy the json and paste it into the text area below.'.format(r.status_code, request.args['url']), 'error')
            return redirect(url_for('requester_index'))
    elif request.args.get('json'):
        return render_template("json.html", responseData=request.args['json'], url='N/A')
    else:
        flash('Please enter a URL or some json before continuing.', 'error')
        return redirect(url_for('requester_index'))


@app.route("/requester/pb", methods=['POST'])
def create_playbook():
    partial_pb_template = """ "jobList": [{
    "id": 1,
    "appCatalogItem": {
        "programName": "Http Client",
        "displayName": "HTTP Client",
        "programVersion": "1.0.0"
    },
    "name": "HTTP Client 1",
    "jobParameterList": [{
        "appCatalogItemParameter": {
            "paramName": "headers"
        },
        "value": "[]"
    }, {
        "appCatalogItemParameter": {
            "paramName": "url"
        },
        "value": "%s"
    }, {
        "appCatalogItemParameter": {
            "paramName": "httpclient_proxy"
        },
        "value": "false"
    }, {
        "appCatalogItemParameter": {
            "paramName": "action"
        },
        "value": "GET"
    }, {
        "appCatalogItemParameter": {
            "paramName": "parameters"
        },
        "value": "[]"
    }, {
        "appCatalogItemParameter": {
            "paramName": "ignore_ssl_trust"
        },
        "value": "false"
    }, {
        "appCatalogItemParameter": {
            "paramName": "body"
        }
    }],
    "locationLeft": -1080.0,
    "locationTop": 170.0,
    "playbookRetryEnabled": false
}, {
    "id": 2,
    "appCatalogItem": {
        "programName": "TCPB - JsonPath v1.0",
        "displayName": "Json Path",
        "programVersion": "2.0.1"
    },
    "name": "Json Path 1",
    "jobParameterList": [{
        "appCatalogItemParameter": {
            "paramName": "column_mapping"
        },
        "value" : "%s"
    }, {
        "appCatalogItemParameter": {
            "paramName": "json_content"
        },
        "value": "#App:1:http_client.response.output_content!String"
    }, {
        "appCatalogItemParameter": {
            "paramName": "null_missing_leaf"
        },
        "value": "false"
    }],
    "locationLeft": -740.0,
    "locationTop": 260.0,
    "playbookRetryEnabled": false
}],
"playbookConnectionList": [{
    "type": "Pass",
    "isCircularOnTarget": false,
    "sourceJobId": 1,
    "targetJobId": 2
}],"""

    full_pb_template = """
{
    "definitionVersion" : "1.0.0",
    "name" : "%s Requester Playbook",
    "panX" : 1392.0,
    "panY" : 20.0,
    "logLevel" : "WARN",
    "description" : "Playbook that makes requests to %s and parses the json.",
    %s
    "playbookTriggerList" : [ ],
    "dateExported" : "1/12/18 7:17 PM"
}"""

    json_paths = json.loads(request.form['jsonPaths'])
    reformatted_json = [{"key": path['name'], "value": path['path']} for path in json_paths]
    output_json = json.dumps(reformatted_json).replace('"', '\\"')

    rendered_partial_pb_template = partial_pb_template % (request.form['url'], output_json)

    return render_template("pb.html", partial_pb=rendered_partial_pb_template, full_pb=full_pb_template % (request.form['url'], request.form['url'], rendered_partial_pb_template))


@app.route("/explore")
def explorer_index():
    return render_template("explorer_index.html", playbooks=playbook_data)


@app.route('/explore/<desired_playbook>')
def playbook_details(desired_playbook):
    for playbook in playbook_data:
        if playbook['name'] == desired_playbook:
            return render_template("playbook_details.html", playbook_details=playbook)


if __name__ == '__main__':
    _prepare_playbook_data()
    app.run(debug=True, use_reloader=True)