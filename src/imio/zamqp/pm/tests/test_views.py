# -*- coding: utf-8 -*-

from plone import api
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.permissions import ModifyPortalContent
from Products.PloneMeeting.config import BARCODE_INSERTED_ATTR_ID
from Products.PloneMeeting.utils import cleanMemoize
from Products.statusmessages.interfaces import IStatusMessage
from imio.zamqp.core.utils import next_scan_id
from imio.zamqp.pm.tests.base import BaseTestCase
from zope.i18n import translate

DEFAULT_SCAN_ID = '013999900000001'


class TestInsertBarcodeView(BaseTestCase):

    def setUp(self):
        super(TestInsertBarcodeView, self).setUp()
        self.view = self.portal.file_pdf.restrictedTraverse('@@insert-barcode')

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
        view_txt = self.portal.file_txt.restrictedTraverse('@@insert-barcode')
        # nothing done and a message is added
        self.assertEqual(IStatusMessage(self.request).show(), [])
        view_txt()
        self.assertIsNone(view_txt.context.scan_id)
        barcode_inserted = getattr(view_txt.context,
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
        corrupt_file_pdf = api.content.create(
            id='corrupt_file_pdf',
            type='annex',
            file=self.corrupt_file_pdf,
            container=self.portal,
            description='File description')
        view = corrupt_file_pdf.restrictedTraverse('@@insert-barcode')
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
        self.assertEqual(next_scan_id(
            file_portal_types=['annex', 'annexDecision']),
            '013999900000002')

    def test_may_insert_barcode(self):
        """Must be able to edit the element to insert the barcode."""
        # Manager may always insert barcode
        manager_user = api.user.get_current()
        self.assertTrue('Manager' in manager_user.getRoles())
        self.assertTrue(self.view.may_insert_barcode())

        # as normal user not able to edit
        login(self.portal, TEST_USER_NAME)
        normal_user = api.user.get_current()
        self.assertFalse(normal_user.has_permission(ModifyPortalContent, self.view.context))
        self.assertFalse(self.view.may_insert_barcode())

        # give user ability to edit element
        self.view.context.manage_setLocalRoles(normal_user.getId(), ('Editor', ))
        # clean borg.localroles
        cleanMemoize(self.portal, prefixes=['borg.localrole.workspace.checkLocalRolesAllowed'])
        self.assertTrue(normal_user.has_permission(ModifyPortalContent, self.view.context))
        self.assertTrue(self.view.may_insert_barcode())
