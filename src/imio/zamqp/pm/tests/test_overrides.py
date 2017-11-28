# -*- coding: utf-8 -*-

from imio.zamqp.pm.tests.base import BaseTestCase


class TestOverrides(BaseTestCase):

    def test_pod_template_generation_context(self):
        """When generating a document from a POD template,
           the generation context contains 'zamqp_utils'."""
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        view = item.restrictedTraverse('@@document-generation')
        # zamqp_utils
        self.assertTrue('zamqp_utils' in view.get_base_generation_context())
        self.assertTrue('scan_id' in view.get_base_generation_context())
        # in addition to values added by PloneMeeting
        self.assertTrue('tool' in view.get_base_generation_context())
        self.assertTrue('meetingConfig' in view.get_base_generation_context())
