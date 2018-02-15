#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import html

from http_request_playbook_creation_ui import http_request_playbook_creation_ui
from .test_http_request_playbook_creation_ui import check_heading


class HttpRequestPlaybookCreationUiTestCase(unittest.TestCase):

    def setUp(self):
        self.app = http_request_playbook_creation_ui.app.test_client()

    def test_converter_index(self):
        rv = self.app.get('/converter')
        check_heading(rv.data.decode())

    def test_empty_post_converter(self):
        rv = self.app.post('/converter/convert', data={'playbookContent': ''}, follow_redirects=True)
        assert "Please paste a playbook below to convert it to a component." in rv.data.decode()
        check_heading(rv.data.decode())

    def test_post_converter(self):
        rv = self.app.post('/converter/convert')

    # TODO: Add more tests for the pb creation step with specific values
