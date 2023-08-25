# -*- coding: utf-8 -*-

from imio.zamqp.pm import testing
from Products.PloneMeeting.tests.PloneMeetingTestCase import PloneMeetingTestCase


DEFAULT_SCAN_ID = u'013999900000001'


class BaseTestCase(PloneMeetingTestCase):

    layer = testing.AMQP_PM_TESTING_PROFILE_FUNCTIONAL

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.maxDiff = None
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # enable docs scanning functionnality in PM
        self.portal.portal_plonemeeting.setEnableScanDocs(True)
