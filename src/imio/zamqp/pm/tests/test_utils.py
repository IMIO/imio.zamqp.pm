# -*- coding: utf-8 -*-

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from imio.zamqp.pm.tests.base import BaseTestCase
from imio.zamqp.pm.tests.base import DEFAULT_SCAN_ID
from imio.zamqp.pm.utils import next_scan_id_pm


class TestUtils(BaseTestCase):

    def test_next_scan_id_pm(self):
        """Will work correctly for annex and annexDecision."""
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        annex = self.addAnnex(item)

        # for now, first scan_id returned
        self.assertEqual(next_scan_id_pm(), DEFAULT_SCAN_ID)

        # store a scan_id on annex1
        annex.scan_id = next_scan_id_pm()
        notify(ObjectModifiedEvent(annex))

        self.assertEqual(annex.scan_id, DEFAULT_SCAN_ID)
        self.assertEqual(next_scan_id_pm(), u'013999900000002')
