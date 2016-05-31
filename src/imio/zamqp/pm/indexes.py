# -*- coding: utf-8 -*-
#
# File: indexes.py
#
# Copyright (c) 2016 by Imio.be
#
# GNU General Public License (GPL)
#

from plone.indexer import indexer
from Products.PloneMeeting.interfaces import IMeetingFile
from Products.PluginIndexes.common.UnIndex import _marker


@indexer(IMeetingFile)
def scan_id(obj):
    """
      Indexes the scan_id on the MeetingFile (annex)
    """
    return obj.scan_id or _marker
