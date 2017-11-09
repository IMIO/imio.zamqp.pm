# -*- coding: utf-8 -*-

from collective.iconifiedcategory.utils import get_category_object
from collective.zamqp.message import Message
from imio.zamqp.pm.tests.base import BaseTestCase
from imio.zamqp.pm.utils import next_scan_id_pm
from plone import api

DEFAULT_SCAN_ID = '013999900000001'

DEFAULT_BODY_PATTERN = """ccopy_reg\n_reconstructor\np1\n(cimio.dataexchange.core.dms\nDeliberation\np2\nc__builtin__\nobject\np3\nNtRp4\n(dp5\nS'_doc'\np6\ng1\n(cimio.dataexchange.core.document\nDocument\np7\ng3\nNtRp8\n(dp9\nS'update_date'\np10\ncdatetime\ndatetime\np11\n(S'\\x07\\xe1\\x0b\\x07\\x0f&\\x13\\x08\\xac\\xe8'\ntRp12\nsS'external_id'\np13\nV{0}\np14\nsS'file_md5'\np15\nV23aebcae4ee8f5134da4fa5523abd3dd\np16\nsS'version'\np17\nI6\nsS'user'\np18\nVtestuser\np19\nsS'client_id'\np20\nV019999\np21\nsS'date'\np22\ng11\n(S'\\x07\\xe1\\x0b\\x07\\x0f&\\x13\\x08\\x99\\\\'\ntRp23\nsS'file_metadata'\np24\n(dp25\nVcreator\np26\nVscanner\np27\nsVscan_hour\np28\nV15:00:00\np29\nsVscan_date\np30\nV2014-11-20\np31\nsVupdate\np32\nI01\nsVfilemd5\np33\nV23aebcae4ee8f5134da4fa5523abd3dd\np34\nsVpc\np35\nVpc-scan01\np36\nsVuser\np37\nVtestuser\np38\nsVfilename\np39\nVREADME.rst\np40\nsVpages_number\np41\nI1\nsVfilesize\np42\nI1284\nssS'type'\np43\nVDELIB\np44\nsbsb."""


class TestConsumer(BaseTestCase):

    def _get_consumer_object(self, scan_id=None):
        """ """
        from imio.zamqp.pm.consumer import IconifiedAnnex

        class TestingIconifiedAnnexConsumer(IconifiedAnnex):
            """Mock the consumer as the file_content method is doing an HTTP request
               to get the file and we do not want that..."""

            @property
            def file_content(self):
                return 'New file content'

        msg = Message(body=DEFAULT_BODY_PATTERN.format(scan_id or '013999900000001'))
        annex_updater = TestingIconifiedAnnexConsumer(folder='', document_type='', message=msg)
        return annex_updater

    def test_consumer_can_not_create(self):
        """The consumer is not done for now to create an annex, only to update one."""
        annex_updater = self._get_consumer_object()
        self.assertIsNone(annex_updater.create_or_update())

    def test_consumer_update(self):
        """Create an item with annexes and update it."""
        annex_updater = self._get_consumer_object()
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        annex1 = self.addAnnex(item)
        annex1_modified = annex1.modified()
        annex1_file_size = annex1.file.getSize()
        annex2 = self.addAnnex(item)
        annex2_modified = annex2.modified()
        annex2_file_size = annex2.file.getSize()

        # nothing is done when annex with relevant scan_id is not found
        annex_updater.create_or_update()
        self.assertEqual(annex1.modified(), annex1_modified)
        self.assertEqual(annex1.file.getSize(), annex1_file_size)
        self.assertEqual(annex2.modified(), annex2_modified)
        self.assertEqual(annex2.file.getSize(), annex2_file_size)

        # now apply a scan_id, reindex annex 'scan_id' index and check
        # correct annex will be updated
        annex1.scan_id = next_scan_id_pm()
        annex1.reindexObject(idxs=['scan_id'])
        self.assertEqual(annex1.scan_id, DEFAULT_SCAN_ID)
        annex2.scan_id = next_scan_id_pm()
        annex2.reindexObject(idxs=['scan_id'])
        self.assertNotEqual(annex2.scan_id, DEFAULT_SCAN_ID)
        # correct annex file was updated
        annex_updater.create_or_update()
        self.assertNotEqual(annex1.modified(), annex1_modified)
        self.assertNotEqual(annex1.file.getSize(), annex1_file_size)
        # annex2 was not updated
        self.assertEqual(annex2.modified(), annex2_modified)
        self.assertEqual(annex2.file.getSize(), annex2_file_size)

    def test_consumer_manage_after_scan_change_annex_type_to(self):
        """When an annex is updated by the consumer, it is possible to change
           it's annex_type, test this.
           This is done defining the after_scan_change_annex_type_to field on the
           used annex_type."""
        annex_updater = self._get_consumer_object()
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        annex = self.addAnnex(item)
        annex_uid = annex.UID()
        annex.scan_id = next_scan_id_pm()
        annex.reindexObject(idxs=['scan_id'])
        original_annex_type = get_category_object(annex, annex.content_category)
        original_annex_type_uid = original_annex_type.UID()
        self.assertEqual(original_annex_type.id, 'financial-analysis')
        self.assertEqual(
            original_annex_type_uid,
            annex.categorized_elements[annex_uid]['category_uid'])

        # nothing done if nothing defined
        self.assertIsNone(original_annex_type.after_scan_change_annex_type_to)
        annex_updater.create_or_update()
        # annex find in catalog and categorized_elements correct
        self.assertTrue(api.content.find(content_category_uid=original_annex_type_uid))
        # categorized_elements
        self.assertEqual(
            original_annex_type_uid,
            annex.categorized_elements[annex_uid]['category_uid'])

        # wrong value in after_scan_change_annex_type_to like a removed annex_type
        # does not break
        original_annex_type.after_scan_change_annex_type_to = 'some_removed_uid'
        annex_updater.create_or_update()
        # annex find in catalog and categorized_elements correct
        self.assertTrue(api.content.find(content_category_uid=original_annex_type_uid))
        # categorized_elements
        self.assertEqual(
            original_annex_type_uid,
            annex.categorized_elements[annex_uid]['category_uid'])

        # get another annex_type and set it as after_scan_change_annex_type_to
        another_annex_type = original_annex_type.aq_parent.get('budget-analysis')
        another_annex_type_uid = another_annex_type.UID()
        original_annex_type.after_scan_change_annex_type_to = another_annex_type.UID()

        # when updated, annex_type is changed
        annex_updater.create_or_update()
        new_annex_type = get_category_object(annex, annex.content_category)
        self.assertEqual(new_annex_type.id, another_annex_type.id)
        # everything is correctly updated, including index and categorized_elements dict
        # index updated
        self.assertTrue(api.content.find(content_category_uid=another_annex_type_uid))
        self.assertFalse(api.content.find(content_category_uid=original_annex_type_uid))
        # categorized_elements
        self.assertEqual(
            another_annex_type_uid,
            annex.categorized_elements[annex_uid]['category_uid'])