# -*- coding: utf-8 -*-

from imio.zamqp.pm.tests.base import BaseTestCase
from Products.PloneMeeting.utils import get_annexes


class TestEvents(BaseTestCase):

    def test_annexes_with_scan_id_are_not_kept_on_item_duplication(self):
        """ """
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        self.addAnnex(item)
        annex = self.addAnnex(item)
        annex.scan_id = '001'
        self.addAnnex(item, relatedTo='item_decision')
        annex_decision = self.addAnnex(item, relatedTo='item_decision')
        annex_decision.scan_id = '002'
        self.assertEqual(len(get_annexes(item)), 4)
        # clone
        newItem = item.clone(copyAnnexes=True, copyDecisionAnnexes=True)
        self.assertEqual(len(get_annexes(newItem)), 2)
        self.assertEqual(
            [anAnnex for anAnnex in get_annexes(newItem)
             if getattr(anAnnex, 'scan_id', None)],
            [])
