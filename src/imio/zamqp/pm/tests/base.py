# -*- coding: utf-8 -*-

from imio.zamqp.pm import testing
from plone import namedfile
from Products.PloneMeeting.tests.PloneMeetingTestCase import PloneMeetingTestCase

import os

DEFAULT_SCAN_ID = u'013999900000001'


class BaseTestCase(PloneMeetingTestCase):

    layer = testing.AMQP_PM_TESTING_PROFILE_FUNCTIONAL

    @property
    def file_txt(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, 'file.txt'), 'r')
        return namedfile.NamedBlobFile(f.read(), filename=u'file.txt')

    @property
    def file_pdf(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, 'file.pdf'), 'r')
        return namedfile.NamedBlobFile(f.read(), filename=u'file.pdf')

    @property
    def corrupt_file_pdf(self):
        current_path = os.path.dirname(__file__)
        f = open(os.path.join(current_path, 'file_corrupt.pdf'), 'r')
        return namedfile.NamedBlobFile(f.read(),
                                       contentType='application/pdf',
                                       filename=u'file_corrupt.pdf')

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.maxDiff = None
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # enable docs scanning functionnality in PM
        self.portal.portal_plonemeeting.setEnableScanDocs(True)
