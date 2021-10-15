# -*- coding: utf-8 -*-

from datetime import datetime
from collective.iconifiedcategory.utils import get_category_object
from collective.zamqp.message import Message
from collective.zamqp.message import MessageArrivedEvent
from imio.zamqp.pm.interfaces import IIconifiedAnnex
from imio.zamqp.pm.interfaces import IImioZamqpPMSettings
from imio.zamqp.pm.testing import NEW_FILE_CONTENT
from imio.zamqp.pm.tests.base import BaseTestCase
from imio.zamqp.pm.tests.base import DEFAULT_SCAN_ID
from imio.zamqp.pm.utils import next_scan_id_pm
from plone import api
from zope.event import notify
from zope.interface import alsoProvides

DEFAULT_BODY_PATTERN = """ccopy_reg\n_reconstructor\np1\n(cimio.dataexchange.core.dms\nDeliberation\np2\nc__builtin__\nobject\np3\nNtRp4\n(dp5\nS'_doc'\np6\ng1\n(cimio.dataexchange.core.document\nDocument\np7\ng3\nNtRp8\n(dp9\nS'update_date'\np10\ncdatetime\ndatetime\np11\n(S'\\x07\\xe1\\x0b\\x07\\x0f&\\x13\\x08\\xac\\xe8'\ntRp12\nsS'external_id'\np13\nV{0}\np14\nsS'file_md5'\np15\nV23aebcae4ee8f5134da4fa5523abd3dd\np16\nsS'version'\np17\nI6\nsS'user'\np18\nVtestuser\np19\nsS'client_id'\np20\nV019999\np21\nsS'date'\np22\ng11\n(S'\\x07\\xe1\\x0b\\x07\\x0f&\\x13\\x08\\x99\\\\'\ntRp23\nsS'file_metadata'\np24\n(dp25\nVcreator\np26\nVscanner\np27\nsVscan_hour\np28\nV15:00:00\np29\nsVscan_date\np30\nV2014-11-20\np31\nsVupdate\np32\nI01\nsVfilemd5\np33\nV23aebcae4ee8f5134da4fa5523abd3dd\np34\nsVpc\np35\nVpc-scan01\np36\nsVuser\np37\nVtestuser\np38\nsVfilename\np39\nVREADME.rst\np40\nsVpages_number\np41\nI1\nsVfilesize\np42\nI1284\nssS'type'\np43\nVDELIB\np44\nsbsb."""


class TestConsumer(BaseTestCase):

    def _get_consumer_object(self, scan_id=None):
        """ """
        from imio.zamqp.pm.consumer import IconifiedAnnex
        msg = Message(body=DEFAULT_BODY_PATTERN.format(scan_id or DEFAULT_SCAN_ID))
        annex_updater = IconifiedAnnex(folder='', document_type='', message=msg)
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

        # correct annex file was updated, including scan attributes
        self.assertIsNone(annex1.scan_date)
        self.assertIsNone(annex1.pages_number)
        self.assertIsNone(annex1.scan_user)
        self.assertIsNone(annex1.scanner)
        annex_updater.create_or_update()
        self.assertNotEqual(annex1.modified(), annex1_modified)
        self.assertNotEqual(annex1.file.getSize(), annex1_file_size)
        self.assertEqual(annex1.scan_date, datetime(2014, 11, 20, 15, 0))
        self.assertEqual(annex1.pages_number, 1)
        self.assertEqual(annex1.scan_user, u'testuser')
        self.assertEqual(annex1.scanner, u'pc-scan01')

        # annex2 was not updated
        self.assertEqual(annex2.modified(), annex2_modified)
        self.assertEqual(annex2.file.getSize(), annex2_file_size)

    def test_consumer_update_annex_with_inserted_barcode(self):
        """Create an item with a PDF annex, insert the barcode then update it.
           This also test that multiple versions are not applied, it fails in
           versioning when scanned file is versioned because of a transaction savepoint failure."""
        pr = api.portal.get_tool('portal_repository')
        api.portal.set_registry_record('version_when_barcode_inserted', True, interface=IImioZamqpPMSettings)
        api.portal.set_registry_record('version_when_scanned_file_reinjected', True, interface=IImioZamqpPMSettings)
        annex_updater = self._get_consumer_object()
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        # use a PDF file
        self.annexFile = u'file_correct.pdf'
        annex = self.addAnnex(item)
        view = annex.restrictedTraverse('@@insert-barcode')
        view()
        self.assertEqual(pr.getHistoryMetadata(annex)._available, [0])
        annex_updater.create_or_update()
        # was not versioned again
        self.assertEqual(pr.getHistoryMetadata(annex)._available, [0])
        # but correctly updated
        self.assertEqual(annex.file.data, NEW_FILE_CONTENT)

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
        original_annex_type.after_scan_change_annex_type_to = another_annex_type_uid

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

    def _item_with_annex_with_scan_id(self):
        """Helper method that creates an item containing an annex with scan_id."""
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        self.annexFile = u'file_correct.pdf'
        annex = self.addAnnex(item)
        annex.scan_id = next_scan_id_pm()
        annex.reindexObject(idxs=['scan_id'])
        return item, annex

    def test_consumer_manage_after_scan_change_to_other_category_group(self):
        """When annex_type is changed, if it is an item annex, it can be changed from
           item_annex to item_decision_annex and the other way round."""
        item, annex = self._item_with_annex_with_scan_id()
        annex_uid = annex.UID()
        annex_decision = self.addAnnex(item, relatedTo='item_decision')
        annex_decision_uid = annex_decision.UID()
        annex_decision.scan_id = next_scan_id_pm()
        annex_decision.reindexObject(idxs=['scan_id'])
        annex_updater = self._get_consumer_object(scan_id=annex.scan_id)
        annex_decision_updater = self._get_consumer_object(scan_id=annex_decision.scan_id)

        # annex
        self.assertEqual(annex.portal_type, 'annex')
        original_annex_type = get_category_object(annex, annex.content_category)
        original_annex_type_uid = original_annex_type.UID()
        self.assertEqual(original_annex_type.id, 'financial-analysis')
        self.assertEqual(
            original_annex_type_uid,
            annex.categorized_elements[annex_uid]['category_uid'])
        self.assertEqual(
            original_annex_type.get_category_group().getId(), 'item_annexes')
        # annex_decision
        self.assertEqual(annex_decision.portal_type, 'annexDecision')
        original_annex_decision_type = get_category_object(annex_decision, annex_decision.content_category)
        original_annex_decision_type_uid = original_annex_decision_type.UID()
        self.assertEqual(original_annex_decision_type.id, 'decision-annex')
        self.assertEqual(
            original_annex_decision_type_uid,
            annex_decision.categorized_elements[annex_decision_uid]['category_uid'])
        self.assertEqual(
            original_annex_decision_type.get_category_group().getId(), 'item_decision_annexes')

        # set the 2 annexes types as after_scan_change_annex_type_to of each other
        original_annex_type.after_scan_change_annex_type_to = original_annex_decision_type_uid
        original_annex_decision_type.after_scan_change_annex_type_to = original_annex_type_uid

        # when updated, annex_type is changed
        # annex
        annex_updater.create_or_update()
        new_annex_type = get_category_object(annex, annex.content_category)
        self.assertEqual(new_annex_type.UID(), original_annex_decision_type_uid)
        # everything is correctly updated, including index and categorized_elements dict
        # portal_type
        self.assertEqual(annex.portal_type, 'annexDecision')
        # index updated
        self.assertTrue(api.content.find(
            content_category_uid=original_annex_decision_type_uid,
            portal_type='annexDecision'))
        # categorized_elements
        self.assertEqual(
            original_annex_decision_type_uid,
            annex.categorized_elements[annex_uid]['category_uid'])

        # annex_decision
        annex_decision_updater.create_or_update()
        new_annex_decision_type = get_category_object(annex_decision, annex_decision.content_category)
        self.assertEqual(new_annex_decision_type.UID(), original_annex_type_uid)
        # everything is correctly updated, including index and categorized_elements dict
        # portal_type
        self.assertEqual(annex_decision.portal_type, 'annex')
        # index updated
        self.assertTrue(api.content.find(
            content_category_uid=original_annex_type_uid, portal_type='annex'))
        # categorized_elements
        self.assertEqual(
            original_annex_type_uid,
            annex_decision.categorized_elements[annex_decision_uid]['category_uid'])

    def test_consumer_message_arrived_event(self):
        """Consumer is called on IMessageArrivedEvent."""
        item, annex = self._item_with_annex_with_scan_id()
        self.assertTrue("/DocChecksum /E1B86A6F99866F3DF1A888178C4F6F94" in annex.file.data)
        msg = Message(body=DEFAULT_BODY_PATTERN.format(DEFAULT_SCAN_ID))
        alsoProvides(msg, IIconifiedAnnex)
        msg.acknowledged = True
        notify(MessageArrivedEvent(msg))
        self.assertEqual(annex.file.data, NEW_FILE_CONTENT)
