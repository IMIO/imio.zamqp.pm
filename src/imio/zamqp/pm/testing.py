# -*- coding: utf-8 -*-
#
# File: testing.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from plone.testing import z2
from plone.testing import zca
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer
from Products.CMFPlone.utils import base_hasattr

import imio.zamqp.pm


# monkey patched version of consumer.IconifiedAnnex.file_content
@property
def patched_file_content(self):
    return 'New file content'


class ImioZamqpPMLayer(PloneWithPackageLayer):

    def setUpZope(self, app, configurationContext):
        from App.config import _config
        if not base_hasattr(_config, 'product_config'):
            _config.product_config = {'imio.zamqp.core': {'ws_url': 'http://localhost:6543', 'ws_password': 'test',
                                                          'ws_login': 'testuser', 'routing_key': '019999',
                                                          'client_id': '019999'}}
        super(ImioZamqpPMLayer, self).setUpZope(app, configurationContext)

AMQP_PM_ZCML = zca.ZCMLSandbox(
    filename="testing.zcml",
    package=imio.zamqp.pm,
    name='PM_ZCML')

AMQP_PM_Z2 = z2.IntegrationTesting(
    bases=(z2.STARTUP, AMQP_PM_ZCML),
    name='AMQP_PM_Z2')


AMQP_PM_TESTING_PROFILE = ImioZamqpPMLayer(
    zcml_filename="testing.zcml",
    zcml_package=imio.zamqp.pm,
    additional_z2_products=['imio.dashboard',
                            'Products.PloneMeeting',
                            'Products.PasswordStrength',
                            'Products.CMFPlacefulWorkflow'],
    gs_profile_id='imio.zamqp.pm:testing',
    name="AMQP_PM_TESTING_PROFILE")


AMQP_PM_TESTING_PROFILE_INTEGRATION = IntegrationTesting(
    bases=(AMQP_PM_TESTING_PROFILE,),
    name="AMQP_PM_TESTING_PROFILE_INTEGRATION")

AMQP_PM_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(AMQP_PM_TESTING_PROFILE,),
    name="AMQP_PM_TESTING_PROFILE_FUNCTIONAL")
