# -*- coding: utf-8 -*-

import os

from plone import api
from plone import namedfile
from plone.app.testing import login

from imio.zamqp.pm import testing
from Products.PloneMeeting.tests.PloneMeetingTestCase import PloneMeetingTestCase


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

        # use default workflow
        wftool = self.portal['portal_workflow']
        wftool.setDefaultChain('simple_publication_workflow')
        wftool.setChainForPortalTypes(
            ('annex', 'annexDecision'),
            ('simple_publication_workflow',))

        api.user.create(
            email='test@test.com',
            username='adminuser',
            password='Secret_123',
        )
        api.user.grant_roles(
            username='adminuser',
            roles=['Manager'],
        )
        login(self.portal, 'adminuser')
        api.content.create(
            id='file_txt',
            type='annex',
            file=self.file_txt,
            container=self.portal,
            description='File description')
        api.content.create(
            id='file_pdf',
            type='annex',
            file=self.file_pdf,
            container=self.portal,
            description='File description')
