# -*- coding: utf-8 -*-
#
# File: events.py
#

from imio.actionspanel.utils import unrestrictedRemoveGivenObject
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.PloneMeeting.utils import get_annexes
from zope.i18n import translate


def onItemDuplicated(original, event):
    '''When an item is duplicated, make sure every annexes with a scan_id are removed.'''
    newItem = event.newItem
    annexes = get_annexes(newItem)
    for annex in annexes:
        if getattr(annex, 'scan_id', None):
            unrestrictedRemoveGivenObject(annex)
            msg = translate('annex_not_kept_because_using_scan_id',
                            mapping={'annexTitle': safe_unicode(annex.Title())},
                            domain='PloneMeeting',
                            context=newItem.REQUEST)
            api.portal.show_message(msg, request=newItem.REQUEST, type='warning')
