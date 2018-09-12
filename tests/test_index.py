#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from playbook_utility import playbook_utility


def check_heading(response):
    """Make sure the heading is shown in a response."""
    assert 'Playbook Utility' in response
    assert 'Helpful tools for working with ThreatConnect playbooks.' in response


def check_index(response):
    """Make sure the response contains everything that should be in the index."""
    check_heading(response)
    assert "HTTP Request Playbook Creator" in response


class IndexTestCase(unittest.TestCase):

    def setUp(self):
        self.app = playbook_utility.app.test_client()

    def test_get_index(self):
        rv = self.app.get('/')
        check_index(rv.data.decode())
