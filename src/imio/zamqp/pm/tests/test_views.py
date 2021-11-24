# -*- coding: utf-8 -*-

from imio.prettylink.interfaces import IPrettyLink
from imio.zamqp.pm.interfaces import IImioZamqpPMSettings
from imio.zamqp.pm.tests.base import BaseTestCase
from imio.zamqp.pm.tests.base import DEFAULT_SCAN_ID
from imio.zamqp.pm.utils import next_scan_id_pm
from plone import api
from Products.CMFCore.permissions import ModifyPortalContent
from Products.PloneMeeting.config import BARCODE_INSERTED_ATTR_ID
from Products.PloneMeeting.utils import cleanMemoize
from Products.statusmessages.interfaces import IStatusMessage
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import ObjectModifiedEvent


class TestInsertBarcodeView(BaseTestCase):

    def setUp(self):
        super(TestInsertBarcodeView, self).setUp()
        self.changeUser('pmManager')
        self.item = self.create('MeetingItem')
        annex_txt = self.addAnnex(self.item)
        annex_pdf = self.addAnnex(self.item, annexFile=self.annexFilePDF)
        self.view = annex_pdf.restrictedTraverse('@@insert-barcode')
        self.view_txt = annex_txt.restrictedTraverse('@@insert-barcode')
        # wipeout portal messages
        IStatusMessage(self.request).show()

    def _check_barcode_inserted_correctly(self):
        """ """
        self.view()
        messages = IStatusMessage(self.request).show()
        translated_msg = translate(u'barcode_inserted',
                                   domain='imio.zamqp.pm',
                                   context=self.request)
        self.assertEqual(messages[-1].message, translated_msg)
        self.assertEqual(self.view.context.scan_id, DEFAULT_SCAN_ID)
        barcode_inserted = getattr(self.view.context,
                                   BARCODE_INSERTED_ATTR_ID,
                                   False)
        self.assertTrue(barcode_inserted)

    def test_barcode_inserted_in_pdf_file(self):
        """Working behavior."""
        self.assertEqual(IStatusMessage(self.request).show(), [])
        self._check_barcode_inserted_correctly()

    def test_file_must_be_pdf(self):
        """ """
        # nothing done and a message is added
        self.assertEqual(IStatusMessage(self.request).show(), [])
        self.view_txt()
        self.assertIsNone(self.view_txt.context.scan_id)
        barcode_inserted = getattr(self.view_txt.context,
                                   BARCODE_INSERTED_ATTR_ID,
                                   False)
        self.assertFalse(barcode_inserted)
        messages = IStatusMessage(self.request).show()
        translated_msg = translate(u'barcode_file_must_be_pdf',
                                   domain='imio.zamqp.pm',
                                   context=self.request)
        self.assertEqual(messages[-1].message, translated_msg)

    def test_barcode_inserted_only_once(self):
        """ """
        self._check_barcode_inserted_correctly()
        # call again
        self.view()
        messages = IStatusMessage(self.request).show()
        translated_msg = translate(u'barcode_already_inserted',
                                   domain='imio.zamqp.pm',
                                   context=self.request)
        self.assertEqual(messages[-1].message, translated_msg)

    def test_corrupted_pdf_does_not_break_view(self):
        """ """
        corrupted_annex = self.addAnnex(self.item, annexFile=self.annexFileCorruptedPDF)
        view = corrupted_annex.restrictedTraverse('@@insert-barcode')
        self.assertEqual(IStatusMessage(self.request).show(), [])
        view()
        self.assertIsNone(view.context.scan_id)
        barcode_inserted = getattr(view.context,
                                   BARCODE_INSERTED_ATTR_ID,
                                   False)
        self.assertFalse(barcode_inserted)
        messages = IStatusMessage(self.request).show()
        translated_msg = translate(u'barcode_insert_error',
                                   domain='imio.zamqp.pm',
                                   context=self.request)
        self.assertEqual(messages[-1].message, translated_msg)

    def test_next_scan_id_after_barcode_inserted(self):
        """After barcode is inserted"""
        self.assertIsNone(self.view.context.scan_id)
        self._check_barcode_inserted_correctly()
        self.assertEqual(self.view.context.scan_id, DEFAULT_SCAN_ID)
        self.assertEqual(next_scan_id_pm(), u'013999900000002')

    def test_may_insert_barcode(self):
        """Must be (Meeting)Manager able to edit the element to insert the barcode."""
        self.assertTrue(self.tool.isManager(self.meetingConfig))
        self.assertTrue(self.view.may_insert_barcode())

        # as normal user, able to edit but not able to insert barcode
        self.changeUser('pmCreator1')
        self.assertTrue(self.member.has_permission(ModifyPortalContent, self.view.context))
        self.assertFalse(self.view.may_insert_barcode())

        # now as MeetingManager
        self.changeUser('pmManager')
        self.view.context.manage_setLocalRoles(self.member.getId(), ('MeetingManager', 'Editor'))
        # clean borg.localroles
        cleanMemoize(self.portal, prefixes=['borg.localrole.workspace.checkLocalRolesAllowed'])
        self.assertTrue(self.member.has_permission(ModifyPortalContent, self.view.context))
        self.assertTrue(self.view.may_insert_barcode())

    def test_leadingIcons_barcode(self):
        """When a barcode is inserted into a file, a relevant leading icon is displayed."""
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        # use a PDF file
        self.annexFile = u'file_correct.pdf'
        annex = self.addAnnex(item)
        view = annex.restrictedTraverse('@@insert-barcode')

        # for now, no barcode
        self.assertFalse('barcode.png' in IPrettyLink(annex).getLink())
        # insert barcode and check
        view()
        self.assertTrue('barcode.png' in IPrettyLink(annex).getLink())

        # if file is updated, the barcode icon is removed
        notify(ObjectModifiedEvent(annex))
        self.assertFalse('barcode.png' in IPrettyLink(annex).getLink())

    def test_annex_version_when_barcode_inserted(self):
        """If parameter version_when_barcode_inserted is True, the annex
           is versionned when the barcode is inserted so it is possible
           to fall back to original file."""
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        # use a PDF file
        self.annexFile = u'file_correct.pdf'

        # no versioning
        annex = self.addAnnex(item)
        view = annex.restrictedTraverse('@@insert-barcode')
        pr = api.portal.get_tool('portal_repository')
        self.assertFalse(
            api.portal.get_registry_record('version_when_barcode_inserted',
                                           interface=IImioZamqpPMSettings))
        view()
        self.assertFalse(pr.getHistoryMetadata(annex))

        # versioning
        api.portal.set_registry_record(
            'version_when_barcode_inserted', True, interface=IImioZamqpPMSettings)
        annex2 = self.addAnnex(item)
        view = annex2.restrictedTraverse('@@insert-barcode')
        view()
        self.assertTrue(pr.getHistoryMetadata(annex2))
        # version 0 is available
        self.assertEqual(pr.getHistoryMetadata(annex2)._available, [0])
        # files are different as original file was saved with version
        old_obj = pr.retrieve(annex2, 0).object
        self.assertNotEqual(old_obj.file.size, annex2.file.size)
