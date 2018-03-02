#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import html

from playbook_utility import playbook_utility


def check_heading(response):
    """Make sure the heading is shown in a response."""
    assert 'Playbook Utility' in response
    assert 'Helpful tools for working with ThreatConnect playbooks.' in response


def check_pb_name_and_description(response):
    assert 'Palo Alto Wildfire Malware Triage (File)' in response
    assert 'users detonate a file in Palo Alto Wildfire' in response


def check_component_name_and_description(response):
    # TODO: implement
    assert '' in response


def check_app_name_and_description(response):
    assert 'JSON Builder' in response
    assert 'Take data of multiple types and output a JSON String.' in response


def check_index(response):
    """Make sure the response contains everything that should be in the index."""
    check_heading(response)
    assert 'Playbooks' in response
    assert 'Components' in response
    assert 'Playbook Apps' in response
    check_pb_name_and_description(response)
    check_component_name_and_description(response)
    check_app_name_and_description(response)


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
        check_pb_name_and_description(rv.data.decode())

    def test_nonexist_page(self):
        """Make sure the page for each playbook is working properly."""
        rv = self.app.get('/explore/foobar', follow_redirects=True)
        assert 'There is no playbook, component, or app with the name foobar. Click on one of the playbooks below to explore it.' in rv.data.decode()

    def test_votes(self):
        rv = self.app.post('/explore/Palo%20Alto%20Wildfire%20Malware%20Triage%20(File)/vote')
        assert '/explore/Palo%20Alto%20Wildfire%20Malware%20Triage%20%28File%29' in rv.location

    def test_votes_db(self):
        # get the initial vote count
        voted_object = playbook_utility.PbObject.query.filter_by(name='Palo Alto Wildfire Malware Triage (File)').first()
        initial_votes = voted_object.votes

        # vote for the playbook
        rv = self.app.post('/explore/Palo%20Alto%20Wildfire%20Malware%20Triage%20(File)/vote')

        # get the object again (yes, this is necesary) and check the vote count
        voted_object = playbook_utility.PbObject.query.filter_by(name='Palo Alto Wildfire Malware Triage (File)').first()
        assert voted_object.votes == initial_votes + 1

    def test_votes_redirect(self):
        rv = self.app.post('/explore/Palo%20Alto%20Wildfire%20Malware%20Triage%20(File)/vote', follow_redirects=True)
        assert 'Download playbook' in rv.data.decode()
        check_pb_name_and_description(rv.data.decode())

    # TODO: Add tests to make sure images are properly shown
