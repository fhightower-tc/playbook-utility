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

    for job in pb_json['jobList']:
        if 'ThreatConnect Custom' in job['appCatalogItem']['displayName']:
            new_custom_metric_docs = dict()
            new_custom_metric_docs['name'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'metric_name')
            new_custom_metric_docs['weight'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'metric_weight')
            new_custom_metric_docs['date'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'metric_date')
            new_custom_metric_docs['value'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'metric_value')
            new_custom_metric_docs['key'] = _find_value_of_parameter_by_name(job['jobParameterList'], 'metric_key')

    return custom_metric_docs


def generate_documentation(playbook_json):
    """Generate documentation for the given playbook."""
    documentation = dict()

    documentation['custom_metrics'] = _generate_custom_metrics_docs(playbook_json)

    return documentation
