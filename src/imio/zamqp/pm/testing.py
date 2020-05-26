# -*- coding: utf-8 -*-
#
# File: testing.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.testing import z2
from plone.testing import zca
from Products.PloneMeeting.testing import PMLayer

import imio.zamqp.pm


# monkey patched version of consumer.IconifiedAnnex.file_content
NEW_FILE_CONTENT = 'New file content'


@property
def patched_file_content(self):
    """ """
    return NEW_FILE_CONTENT


class ImioZamqpPMLayer(PMLayer):
    """ """


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
