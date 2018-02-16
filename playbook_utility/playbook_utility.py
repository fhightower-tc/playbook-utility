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


@app.route("/converter")
def converter_index():
    return render_template('converter_index.html')


def _convert_to_component(playbook_dict):
    """Convert the playbook to a component."""
    playbook_dict['type'] = 'Pipe'

    # todo: check if there is already an id of 53
    new_trigger_id = 53

    # replace all of the links to an from the trigger
    original_trigger_id = playbook_dict['playbookTriggerList'][0]['id']
    for link in playbook_dict['playbookConnectionList']:
        if link['targetTriggerId'] == original_trigger_id:
            link['targetTriggerId'] = new_trigger_id
        elif link.get('sourceTriggerId') == original_trigger_id:
            link['sourceTriggerId'] = new_trigger_id

    playbook_dict['playbookTriggerList'] = [{
        "id" : new_trigger_id,
        "name" : "Component Trigger",
        "type" : "PipeConfig",
        "eventType" : "Create",
        "httpBasicAuthEnable" : False,
        "anyOrg" : True,
        "orFilters" : False,
        "fireOnDuplicate" : False,
        "renderBodyAsTip" : False,
        "pipeInputParams" : "[{\"label\":\"b\",\"dataType\":\"String\",\"playbookDataType\":\"String\",\"required\":false,\"name\":\"a\",\"encrypted\":false,\"hidden\":false,\"hasDollarVariables\":false,\"playbookVariable\":false,\"validValuesList\":[\"${TEXT}\",\"${KEYCHAIN}\"]}]",
        "pipeOutputParams" : "[{\"key\":\"c\",\"value\":\"d\",\"displayValue\":\"d\"}]"
    }]
    return playbook_dict


@app.route("/converter/convert", methods=['POST'])
def convert_pb():
    playbook = request.form['playbookContent']

    if playbook == '' or playbook == None:
        flash('Please paste a playbook below to convert it to a component.', 'error')
        return redirect(url_for('converter_index'))

    # TODO: see if there is a better way to handle the escaped quotation marks other than the replacements below... if there is not, add some comments explaining them

    playbook = playbook.replace('\\"', '=+=+=')
    playbook_dict = json.loads(playbook)
    component = _convert_to_component(playbook_dict)

    return render_template('convert.html', converted_playbook=json.dumps(component).replace('=+=+=', '\\"'))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
