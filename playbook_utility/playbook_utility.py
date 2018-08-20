#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json
import os
try:
    from StringIO import StringIO as ZipIO
except:
    from io import BytesIO as ZipIO
import tempfile
import zipfile

from flask import flash, Flask, render_template, redirect, request, url_for
import playbook_documenter
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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/requester")
def requester_index():
    return render_template("requester_index.html")


@app.route("/requester/json", methods=['GET', 'POST'])
def parse_json():
    url = None

    # handle GET requests (this is to support the example link on the index page)
    if request.method == 'GET':
        if request.args.get('url'):
            url = request.args['url']
    # handle POST requests
    else:
        if request.form.get('url'):
            url = request.form['url']
        elif request.form.get('json'):
            return render_template("json.html", responseData=request.form['json'], url='N/A')

    if url:
        r = requests.get(url)

        if r.ok:
            return render_template("json.html", responseData=r.text, url=url)
        else:
            flash('Got a {} response code from {}. Please try another site or copy the json and paste it into the text area below.'.format(r.status_code, url), 'error')
            return redirect(url_for('requester_index'))
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


@app.route("/documenter")
def documenter_index():
    return render_template("documenter.html")


@app.route("/docs", methods=['POST'])
def document_playbook():
    if request.form.get('playbook'):
        html_docs = playbook_documenter.generate_documentation(request.form['playbook'], output_format='html')
        markdown_docs = playbook_documenter.generate_documentation(request.form['playbook'], output_format='markdown')
        return render_template("documenter.html", html_docs=html_docs, markdown_docs=markdown_docs)
    else:
        flash('Please paste the text for a playbook/component to create documentation for it.', 'error')
        return render_template("documenter.html")


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
