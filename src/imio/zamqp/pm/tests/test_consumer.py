# -*- coding: utf-8 -*-

from collective.zamqp.message import Message
from imio.zamqp.core.utils import next_scan_id
from imio.zamqp.pm.tests.base import BaseTestCase

DEFAULT_SCAN_ID = '013999900000001'

DEFAULT_BODY_PATTERN = """ccopy_reg\n_reconstructor\np1\n(cimio.dataexchange.core.dms\nDeliberation\np2\nc__builtin__\nobject\np3\nNtRp4\n(dp5\nS'_doc'\np6\ng1\n(cimio.dataexchange.core.document\nDocument\np7\ng3\nNtRp8\n(dp9\nS'update_date'\np10\ncdatetime\ndatetime\np11\n(S'\\x07\\xe1\\x0b\\x07\\x0f&\\x13\\x08\\xac\\xe8'\ntRp12\nsS'external_id'\np13\nV{0}\np14\nsS'file_md5'\np15\nV23aebcae4ee8f5134da4fa5523abd3dd\np16\nsS'version'\np17\nI6\nsS'user'\np18\nVtestuser\np19\nsS'client_id'\np20\nV019999\np21\nsS'date'\np22\ng11\n(S'\\x07\\xe1\\x0b\\x07\\x0f&\\x13\\x08\\x99\\\\'\ntRp23\nsS'file_metadata'\np24\n(dp25\nVcreator\np26\nVscanner\np27\nsVscan_hour\np28\nV15:00:00\np29\nsVscan_date\np30\nV2014-11-20\np31\nsVupdate\np32\nI01\nsVfilemd5\np33\nV23aebcae4ee8f5134da4fa5523abd3dd\np34\nsVpc\np35\nVpc-scan01\np36\nsVuser\np37\nVtestuser\np38\nsVfilename\np39\nVREADME.rst\np40\nsVpages_number\np41\nI1\nsVfilesize\np42\nI1284\nssS'type'\np43\nVDELIB\np44\nsbsb."""


class TestConsumer(BaseTestCase):

    def setUp(self):
        super(TestConsumer, self).setUp()

    def _get_consumer_object(self, scan_id=None):
        """ """
        from imio.zamqp.pm.consumer import IconifiedAnnex
        msg = Message(body=DEFAULT_BODY_PATTERN.format(scan_id or '013999900000001'))
        annex_updater = IconifiedAnnex(folder='', document_type='', message=msg)
        return annex_updater

    def test_consumer_can_not_create(self):
        """The consumer is not done for now to create an annex, only to update one."""
        annex_updater = self._get_consumer_object()
        self.assertIsNone(annex_updater.create_or_update())

    def test_consumer_update(self):
        """Create an item with annexes and update it."""
        # annex_updater = self._get_consumer_object()
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        annex = self.addAnnex(item)
        # annex_modified = annex.modified()
        # annex_file_size = annex.file.getSize()
        annex.scan_id = next_scan_id()
        annex.reindexObject(idxs=['scan_id'])
