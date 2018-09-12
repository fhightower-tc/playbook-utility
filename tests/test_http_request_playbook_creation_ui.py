#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from playbook_utility import playbook_utility


def check_heading(response):
    """Make sure the heading is shown in a response."""
    assert 'Playbook Utility' in response
    assert 'Helpful tools for working with ThreatConnect playbooks.' in response


def check_requester_index(response):
    """Make sure the response contains everything that should be in the index."""
    check_heading(response)
    assert "Try 'https://ioc-fang.github.io/datasets/fang.json'" in response


class HttpRequestPlaybookCreationUiTestCase(unittest.TestCase):

    def setUp(self):
        self.app = playbook_utility.app.test_client()

    def test_get_index(self):
        rv = self.app.get('/requester')
        check_requester_index(rv.data.decode())

    def test_json_parse(self):
        rv = self.app.post('requester/json', data={'url': 'https://ioc-fang.github.io/datasets/fang.json'})
        check_heading(rv.data.decode())
        assert '[.]' in rv.data.decode()
        assert 'xxxxx://' in rv.data.decode()
        assert 'Name of playbook output variable:' in rv.data.decode()

    def test_empty_json_parse(self):
        """Make sure an error message is shown if no content is given to the json path."""
        rv = self.app.post('requester/json', follow_redirects=True)
        check_requester_index(rv.data.decode())
        assert "Please enter a URL or some json before continuing." in rv.data.decode()

    def test_blank_pb_creation(self):
        """Make sure that the blank playbook template created by this app is correct."""
        rv = self.app.post('requester/pb', data={
            'jsonPaths': '[]',
            'url': ''
        })
        check_heading(rv.data.decode())
        assert 'Complete Playbook' in rv.data.decode()
        assert 'Partial Playbook' in rv.data.decode()
        assert '&#34;definitionVersion&#34; : &#34;1.0.0&#34;,' in rv.data.decode()

    # TODO: Add more tests for the pb creation step with specific values
