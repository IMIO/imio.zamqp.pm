# -*- coding: utf-8 -*-
#
# File: indexes.py
#
# Copyright (c) 2016 by Imio.be
#
# GNU General Public License (GPL)
#

from Acquisition import aq_base
from plone.indexer import indexer
from Products.Archetypes.interfaces.base import IBaseObject
from Products.PluginIndexes.common.UnIndex import _marker


@indexer(IBaseObject)
def scan_id(obj):
    """
      Indexes the scan_id on the MeetingFile (annex)
    """
    return aq_base(obj).scan_id or _marker
