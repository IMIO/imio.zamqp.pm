# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2017 by Imio.be
#
# GNU General Public License (GPL)
#


import logging
from imio.helpers.catalog import addOrUpdateIndexes
from imio.helpers.catalog import addOrUpdateColumns

logger = logging.getLogger('imio.zamqp.pm: setuphandlers')

indexInfos = {
    'scan_id': ('FieldIndex', {}),
}
columnInfos = ('scan_id', )


def postInstall(context):
    """Called at the end of the setup process. """
    if isNotImioZamqpPmProfile(context):
        return
    site = context.getSite()

    addOrUpdateIndexes(site, indexInfos)
    addOrUpdateColumns(site, columnInfos)


def isNotImioZamqpPmProfile(context):
    return context.readDataFile("imio_zamqp_pm_default_marker.txt") is None
