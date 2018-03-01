#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import html

from playbook_utility import playbook_utility


def check_heading(response):
    """Make sure the heading is shown in a response."""
    assert 'Playbook Utility' in response
    assert 'Helpful tools for working with ThreatConnect playbooks.' in response


def check_pb_name_and_details(response):
    """Make sure the response contains everything that should be in the index."""
    check_heading(response)
    assert 'Palo Alto Wildfire Malware Triage (File)' in response
    assert 'users detonate a file in Palo Alto Wildfire' in response


def check_index(response):
    """Make sure the response contains everything that should be in the index."""
    check_heading(response)
    check_pb_name_and_details(response)
    assert 'Playbooks' in response
    assert 'Components' in response
    assert 'Playbook Apps' in response


class ExplorerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = playbook_utility.app.test_client()

    def test_get_index(self):
        rv = self.app.get('/explore')
        check_index(rv.data.decode())

    def test_detail_page_view(self):
        """Make sure the page for each playbook is working properly."""
        rv = self.app.get('/explore/Palo%20Alto%20Wildfire%20Malware%20Triage%20(File)')
        assert 'Download playbook' in rv.data.decode()
        check_pb_name_and_details(rv.data.decode())

    def test_nonexist_page(self):
        """Make sure the page for each playbook is working properly."""
        rv = self.app.get('/explore/foobar', follow_redirects=True)
        assert 'There is no playbook with the name foobar. Click on one of the playbooks below to explore it.' in rv.data.decode()

    # TODO: Add tests to make sure images are properly shown
