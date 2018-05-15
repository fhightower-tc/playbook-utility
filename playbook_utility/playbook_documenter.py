#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


def _find_value_of_parameter_by_name(parameter_list, name):
    for parameter in parameter_list:
        if parameter['appCatalogItemParameter']['paramName'] == name:
            return parameter.get('value')
            break
    return None


def _generate_custom_metrics_docs(playbook_json):
    """Generate docs for any custom metrics referenced in the playbook."""
    custom_metric_docs = list()

    for job in playbook_json['jobList']:
        if 'ThreatConnect Custom' in job['appCatalogItem']['displayName']:
            new_custom_metric_docs = dict()
            new_custom_metric_docs['name'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'metric_name')
            new_custom_metric_docs['weight'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'metric_weight')
            new_custom_metric_docs['date'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'metric_date')
            new_custom_metric_docs['value'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'metric_value')
            new_custom_metric_docs['key'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'metric_key')
            custom_metric_docs(new_custom_metric_docs)

    return custom_metric_docs


def _generate_datastore_docs(playbook_json):
    """Generate documentation for any datastores used by the playbook."""
    datastore_docs = list()

    for job in playbook_json['jobList']:
        if job['appCatalogItem']['displayName'] == 'Data Store':
            new_datastore_docs = dict()
            new_datastore_docs['type_name'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'type_name')
            new_datastore_docs['domain_type'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'domain_type')
            new_datastore_docs['db_method'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'db_method')
            new_datastore_docs['path'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'path')
            new_datastore_docs['request_entity'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'request_entity')
            new_datastore_docs['organization_name'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'organization_name')
            datastore_docs.append(new_datastore_docs)

    return datastore_docs


def _handle_variable_parameter_value(variable_parameter_value, existing_parameters):
    """Parse the details about a variable parameter."""
    variable_name_pattern = '\$\{(?:ORGANIZATION|USER):(?:KEYCHAIN|TEXT):(.*?)}'
    variable_type_pattern = '\$\{(?:ORGANIZATION|USER):(KEYCHAIN|TEXT):'
    new_variable_name = re.findall(variable_name_pattern, variable_parameter_value)[0]
    new_variable_type = re.findall(variable_type_pattern, variable_parameter_value)[0].lower()

    for parameter in existing_parameters:
        if new_variable_name == parameter['name'] and new_variable_type == parameter['type']:
            return

    new_variable = {
        'type': new_variable_type,
        'name': new_variable_name
    }

    return new_variable


def _generate_variable_docs(playbook_json):
    """Generate documentation for any variables used by the playbook."""
    variable_docs = dict()

    for job in playbook_json['jobList']:
        if job.get('jobParameterList'):
            for parameter in job['jobParameterList']:
                if parameter.get('value'):
                    if '${USER:' in parameter['value']:
                        if not variable_docs.get('user_variables'):
                            variable_docs['user_variables'] = list()
                        new_variable_docs = _handle_variable_parameter_value(parameter['value'], variable_docs['user_variables'])
                        if new_variable_docs is not None:
                            variable_docs['user_variables'].append(new_variable_docs)
                    elif '${ORGANIZATION:' in parameter['value']:
                        if not variable_docs.get('org_variables'):
                            variable_docs['org_variables'] = list()
                        new_variable_docs = _handle_variable_parameter_value(parameter['value'], variable_docs['org_variables'])
                        if new_variable_docs is not None:
                            variable_docs['org_variables'].append(new_variable_docs)

    return variable_docs


def _generate_internal_variables(playbook_json):
    """Generate documentation for all of the variables which are declared within the app."""
    internal_variable_docs = list()

    for job in pb_json['jobList']:
        if 'SetVariable' in job['appCatalogItem']['programName']:
            variable_mappings = json.loads(_find_value_of_parameter_by_name(job['jobParameterList'], 'variable_mapping'))
            internal_variable_docs.extend(variable_mappings)

    return internal_variable_docs


def generate_documentation(playbook_json):
    """Generate documentation for the given playbook."""
    documentation = dict()

    custom_metric_docs = _generate_custom_metrics_docs(playbook_json)
    if custom_metric_docs:
        documentation['custom_metrics'] = custom_metric_docs

    datastore_docs = _generate_datastore_docs(playbook_json)
    if datastore_docs:
        documentation['datastores'] = datastore_docs

    variable_docs = _generate_variable_docs(playbook_json)
    if variable_docs:
        documentation['variables'] = variable_docs

    internal_variables = _generate_internal_variables(playbook_json)
    if internal_variables:
        documentation['internal_variables'] = internal_variables

    return documentation
