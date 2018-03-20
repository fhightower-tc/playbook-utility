#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
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


def _read_data(tmp_dir_name, object_type):
    # TODO: A lot of the code in this function can be consolidated... I haven't taken the time to do this yet, but it needs to be done eventually
    object_data = list()

    # find the base pb path as well as all of the playbook directories
    for path, dirs, files in os.walk(os.path.join(tmp_dir_name, 'threatconnect-playbooks-master/{}'.format(object_type))):
        object_base_path = path
        object_dirs = dirs
        break

    # handle each playbook
    for object_dir in object_dirs:
        for path, dirs, files in os.walk(os.path.join(object_base_path, object_dir)):
            this_object_data = dict()
            if object_type == 'playbooks' or object_type == 'components':
                for file_ in files:
                    if file_.lower() == 'readme.md':
                        with open(os.path.join(path, file_)) as f:
                            this_object_data['readme'] = f.read()
                    elif file_.lower().endswith('.pbx'):
                        with open(os.path.join(path, file_)) as f:
                            pb_json = json.load(f)
                            this_object_data['name'] = pb_json['name']

                            if pb_json.get('description'):
                                this_object_data['description'] = pb_json['description']
                            else:
                                this_object_data['description'] = 'n/a'
                            this_object_data['pb_file_name'] = file_
                            this_object_data['raw_json'] = json.dumps(pb_json, indent=4)
                            this_object_data['last_updated'] = str(datetime.date.today())

                        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./static/{}/{}".format(object_type, file_))), 'w') as f:
                            f.write(json.dumps(pb_json, indent=4))

                # if there is an `images` directory in the playbook's directory, pull out all of those images
                if 'images' in dirs:
                    for path, dirs, files in os.walk(os.path.join(object_base_path, object_dir, 'images')):
                        for file_ in files:
                            if file_.lower().endswith('.jpg') or file_.lower().endswith('.png'):
                                if not this_object_data.get('images'):
                                    this_object_data['images'] = list()
                                image_file_text = str()
                                with open(os.path.join(path, file_), 'rb') as f:
                                    image_file_text = f.read()

                                with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./static/{}_images/{}".format(object_type, file_))), 'wb') as f:
                                    f.write(image_file_text)

                                this_object_data['images'].append(file_)
            elif object_type == 'apps':
                for file_ in files:
                    if file_.lower() == 'readme.md':
                        with open(os.path.join(path, file_)) as f:
                            this_object_data['readme'] = f.read()
                    elif file_.lower() == 'install.json':
                        with open(os.path.join(path, file_)) as f:
                            install_json = json.load(f)
                            if install_json.get('note'):
                                this_object_data['description'] = install_json['note']
                            this_object_data['name'] = install_json['displayName']
                            this_object_data['last_updated'] = str(datetime.date.today())
                    # this handles apps packaged from http://tcex.hightower.space/
                    elif file_.lower() == '.bumpversion.cfg':
                        # todo: add a check to make sure there is only one directory found here
                        app_dir = [dir_ for dir_ in dirs if not dir_.startswith('test')][0]
                        with open(os.path.join(path, app_dir, 'install.json')) as f:
                            install_json = json.load(f)
                            if install_json.get('note'):
                                this_object_data['description'] = install_json['note']
                            this_object_data['name'] = install_json['displayName']
                            this_object_data['last_updated'] = str(datetime.date.today())

                # if there is an `images` directory in the playbook's directory, pull out all of those images
                if 'images' in dirs:
                    for path, dirs, files in os.walk(os.path.join(object_base_path, object_dir, 'images')):
                        for file_ in files:
                            if file_.lower().endswith('.jpg') or file_.lower().endswith('.png'):
                                if not this_object_data.get('images'):
                                    this_object_data['images'] = list()
                                image_file_text = str()
                                with open(os.path.join(path, file_), 'rb') as f:
                                    image_file_text = f.read()

                                with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./static/{}_images/{}".format(object_type, file_))), 'wb') as f:
                                    f.write(image_file_text)

                                this_object_data['images'].append(file_)
            break

        if this_object_data != {}:
            object_data.append(this_object_data)

    return object_data


def _update_data():
    """Update the list of publicly available playbooks."""
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        response = requests.get('https://github.com/ThreatConnect-Inc/threatconnect-playbooks/archive/master.zip')
        with zipfile.ZipFile(ZipIO(response.content)) as pb_zip:
            pb_zip.extractall(tmp_dir_name)

            playbook_data = _read_data(tmp_dir_name, 'playbooks')
            component_data = _read_data(tmp_dir_name, 'components')
            app_data = _read_data(tmp_dir_name, 'apps')

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./playbooks.json")), 'w+') as f:
        json.dump(playbook_data, f)

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./components.json")), 'w+') as f:
        json.dump(component_data, f)

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./apps.json")), 'w+') as f:
        json.dump(app_data, f)

    return playbook_data, component_data, app_data


def _prepare_data():
    """Create a data structure with all of the publicly available playbooks, components, and apps."""
    try:
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./playbooks.json"))) as f:
            existing_pb_data = json.load(f)

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./components.json"))) as f:
            existing_component_data = json.load(f)

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./apps.json"))) as f:
            existing_app_data = json.load(f)
    except FileNotFoundError:
        return _update_data()
    else:
        # check the last updated date of the first entry
        if existing_pb_data[0]['last_updated'] == str(datetime.date.today()):
            return existing_pb_data, existing_component_data, existing_app_data
        else:
            return _update_data()


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
    return render_template("explorer_index.html", playbooks=playbook_data, components=component_data, apps=app_data)


def get_votes_json():
    """Read and return the votes.json file."""
    try:
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./votes.json")), 'r') as f:
            votes_dict = json.load(f)
    except FileNotFoundError:
        votes_dict = dict()
    return votes_dict


def update_votes(new_votes_dict):
    """Update the votes data."""
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "./votes.json")), 'w+') as f:
        json.dump(new_votes_dict, f)


@app.route('/explore/<desired_object>/vote', methods=['POST'])
def record_vote(desired_object):
    votes_dict = get_votes_json()
    votes_dict[desired_object] = (votes_dict[desired_object] + 1)
    update_votes(votes_dict)
    return redirect(url_for('explore_details', desired_object=desired_object))


def get_votes(object_name):
    """Get the number of votes for the given object."""
    votes_dict = get_votes_json()
    if votes_dict.get(object_name):
        return votes_dict[object_name]
    else:
        votes_dict[object_name] = 0
        update_votes(votes_dict)
        return 0


@app.route('/explore/<desired_object>')
def explore_details(desired_object):
    votes = get_votes(desired_object)

    # TODO: there is probably a better way to determine whether the object is a playbook, component, or playbook app
    for playbook in playbook_data:
        if playbook['name'] == desired_object:
            return render_template('explore_details.html', details=playbook, votes=votes, image_dir='playbooks_images')

    for component in component_data:
        if component['name'] == desired_object:
            return render_template('explore_details.html', details=component, votes=votes, image_dir='components_images')

    for app in app_data:
        if app['name'] == desired_object:
            return render_template('explore_details.html', details=app, votes=votes, image_dir='apps_images')

    flash('There is no playbook, component, or app with the name {}. Click on one of the playbooks below to explore it.'.format(desired_object), 'error')
    return redirect(url_for('explorer_index'))


# this needs to be put here so that the app will run properly in heroku
playbook_data, component_data, app_data = _prepare_data()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
