#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from http_request_playbook_creation_ui import http_request_playbook_creation_ui


class HttpRequestPlaybookCreationUiTestCase(unittest.TestCase):

    def setUp(self):
        self.app = http_request_playbook_creation_ui.app.test_client()

    def test_get_index(self):
        rv = self.app.get('/')
        self.assertIn('HTTP Request Playbook Creation UI', rv.data.decode())
        self.assertIn('UI for creating http request playbook.', rv.data.decode())
