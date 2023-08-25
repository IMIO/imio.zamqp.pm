# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2017 by Imio.be
#
# GNU General Public License (GPL)
#


import logging


logger = logging.getLogger('imio.zamqp.pm: setuphandlers')


def postInstall(context):
    """Called at the end of the setup process. """
    if isNotImioZamqpPmProfile(context):
        return


def isNotImioZamqpPmProfile(context):
    return context.readDataFile("imio_zamqp_pm_default_marker.txt") is None
