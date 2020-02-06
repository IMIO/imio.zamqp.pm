# -*- coding: utf-8 -*-
#
# File: events.py
#

from imio.actionspanel.utils import unrestrictedRemoveGivenObject
from Products.PloneMeeting.utils import get_annexes


def onItemDuplicated(original, event):
    '''When an item is duplicated, make sure every annexes with a scan_id are removed.'''
    newItem = event.newItem
    annexes = get_annexes(newItem)
    for annex in annexes:
        if getattr(annex, 'scan_id', None):
            unrestrictedRemoveGivenObject(annex)
