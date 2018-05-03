#!/usr/bin/env python
# -*- coding: utf-8 -*-


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


def generate_documentation(playbook_json):
    """Generate documentation for the given playbook."""
    documentation = dict()

    custom_metric_docs = _generate_custom_metrics_docs(playbook_json)
    if custom_metric_docs:
        documentation['custom_metrics'] = custom_metric_docs

    datastore_docs = _generate_datastore_docs(playbook_json)
    if datastore_docs:
        documentation['datastores'] = datastore_docs

    return documentation
