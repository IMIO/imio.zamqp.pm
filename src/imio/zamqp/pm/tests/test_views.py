# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from imio.prettylink.interfaces import IPrettyLink
from imio.zamqp.pm.interfaces import IImioZamqpPMSettings
from imio.zamqp.pm.tests.base import BaseTestCase
from imio.zamqp.pm.tests.base import DEFAULT_SCAN_ID
from imio.zamqp.pm.utils import next_scan_id_pm
from plone import api
from Products.CMFCore.permissions import ModifyPortalContent
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
        self.annex_txt = self.addAnnex(self.item)
        self.annex_pdf = self.addAnnex(self.item, annexFile=self.annexFilePDF)
        self.view = self.annex_pdf.restrictedTraverse('@@insert-barcode')
        self.view_txt = self.annex_txt.restrictedTraverse('@@insert-barcode')
        # wipeout portal messages
        IStatusMessage(self.request).show()

    def _check_barcode_inserted_correctly(self):
        """ """
        self.assertIsNone(self.view.context.scan_id)
        self.view()
        messages = IStatusMessage(self.request).show()
        translated_msg = translate(u'barcode_inserted',
                                   domain='imio.zamqp.pm',
                                   context=self.request)
        self.assertEqual(messages[-1].message, translated_msg)
        self.assertEqual(self.view.context.scan_id, DEFAULT_SCAN_ID)

    def test_barcode_inserted_in_pdf_file(self):
        """Working behavior."""
        self.assertEqual(IStatusMessage(self.request).show(), [])
        self._check_barcode_inserted_correctly()

    def test_file_must_be_pdf(self):
        """ """
        # nothing done and a message is added
        self.assertEqual(IStatusMessage(self.request).show(), [])
        self.assertIsNone(self.view_txt.context.scan_id)
        self.view_txt()
        self.assertIsNone(self.view_txt.context.scan_id)
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
        self.assertIsNone(view.context.scan_id)
        view()
        self.assertIsNone(view.context.scan_id)
        messages = IStatusMessage(self.request).show()
        translated_msg = translate(u'barcode_insert_error',
                                   domain='imio.zamqp.pm',
                                   context=self.request)
        self.assertEqual(messages[-1].message, translated_msg)

    def test_next_scan_id_after_barcode_inserted(self):
        """After barcode is inserted"""
        self._check_barcode_inserted_correctly()
        self.assertEqual(self.view.context.scan_id, DEFAULT_SCAN_ID)
        self.assertEqual(next_scan_id_pm(), u'013999900000002')

    def test_may_insert_barcode(self):
        """Must be (Meeting)Manager able to edit the element to insert the barcode."""
        cfg = self.meetingConfig
        self.assertTrue(self.tool.isManager(cfg))
        self.assertTrue(self.view.may_insert_barcode())

        # as normal user, able to edit but not able to insert barcode
        self.changeUser('pmCreator1')
        self.assertFalse(cfg.getAnnexEditorMayInsertBarcode())
        self.assertTrue(self.member.has_permission(ModifyPortalContent, self.view.context))
        self.assertFalse(self.view.may_insert_barcode())
        self.assertRaises(Unauthorized, self.view)

        # now as MeetingManager
        self.changeUser('pmManager')
        self.view.context.manage_setLocalRoles(self.member.getId(), ('MeetingManager', 'Editor'))
        # clean borg.localroles
        cleanMemoize(self.portal, prefixes=['borg.localrole.workspace.checkLocalRolesAllowed'])
        self.assertTrue(self.member.has_permission(ModifyPortalContent, self.view.context))
        self.assertTrue(self.view.may_insert_barcode())

        # when MeetingConfig.annexEditorMayInsertBarcode is True, an editor may insert barcode
        self.changeUser('pmCreator1')
        cfg.setAnnexEditorMayInsertBarcode(True)
        # clean borg.localroles
        cleanMemoize(self.portal, prefixes=['borg.localrole.workspace.checkLocalRolesAllowed'])
        self.assertTrue(self.member.has_permission(ModifyPortalContent, self.view.context))
        self.assertTrue(self.view.may_insert_barcode())
        self.view()
        self.assertEqual(self.catalog(scan_id='013999900000001')[0].UID, self.view.context.UID())

        # when MeetingConfig.ownerMayDeleteAnnexDecision is True, owner may insert barcode
        self.assertFalse(cfg.getOwnerMayDeleteAnnexDecision())
        self.proposeItem(self.item)
        self.assertFalse(self.member.has_permission(ModifyPortalContent, self.view.context))
        self.assertFalse(self.view.may_insert_barcode())
        decision_annex = self.addAnnex(self.item, relatedTo='item_decision', annexFile=self.annexFilePDF)
        view = decision_annex.restrictedTraverse('@@insert-barcode')
        self.assertFalse(view.may_insert_barcode())
        cfg.setOwnerMayDeleteAnnexDecision(True)
        self.assertTrue(view.may_insert_barcode())
        view()
        self.assertEqual(self.catalog(scan_id='013999900000002')[0].UID, decision_annex.UID())

    def test_insert_barcode_batch_action(self):
        """Test the @@insert-barcode-batch-action."""
        cfg = self.meetingConfig
        cfg.setAnnexEditorMayInsertBarcode(True)
        self.changeUser('pmCreator1')
        self.request['form.widgets.uids'] = u'{0},{1}'.format(
            self.view.context.UID(), self.view_txt.context.UID())
        self.request.form['form.widgets.uids'] = self.request['form.widgets.uids']
        form = self.item.restrictedTraverse('@@insert-barcode-batch-action')
        # action must be enabled
        self.assertFalse(form.available())
        self.assertRaises(Unauthorized, form.update)
        cfg.setEnabledAnnexesBatchActions(('insert-barcode', ))
        self.assertTrue(form.available())
        form.update()
        self.assertEqual(len(form.brains), 2)
        self.assertIsNone(self.annex_txt.scan_id)
        self.assertIsNone(self.annex_pdf.scan_id)
        form.handleApply(form, None)
        self.assertIsNone(self.annex_txt.scan_id)
        self.assertEqual(self.annex_pdf.scan_id, '013999900000001')

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
