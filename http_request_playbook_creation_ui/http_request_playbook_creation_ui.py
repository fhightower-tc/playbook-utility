#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

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


@app.route("/")
def index():
    # request.form['text']
    return render_template("index.html")


@app.route("/json")
def parse_json():
    r = requests.get(request.args['domain'])

    if r.ok:
        return render_template("json.html", responseData=r.text, domain=request.args['domain'])
    else:
        print("Error requesting {}: {}".format(request.args['domain'], r.text))
        # TODO: raise better error message here
        return redirect(url_for('index'))


@app.route("/pb", methods=['POST'])
def create_playbook():
    playbook_template = """ "jobList": [{
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

    json_paths = json.loads(request.form['jsonPaths'])
    reformatted_json = [{"key": path['name'], "value": path['path']} for path in json_paths]
    output_json = json.dumps(reformatted_json).replace('"', '\\"')

    return (playbook_template % (request.form['domain'], output_json))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
