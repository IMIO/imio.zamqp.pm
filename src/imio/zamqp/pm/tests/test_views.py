# -*- coding: utf-8 -*-

from plone import api
from Products.PloneMeeting.config import BARCODE_INSERTED_ATTR_ID
from Products.statusmessages.interfaces import IStatusMessage
from imio.zamqp.pm.tests.base import BaseTestCase


class TestInsertBarcodeView(BaseTestCase):

    def setUp(self):
        super(TestInsertBarcodeView, self).setUp()
        self.view = self.portal.file_pdf.restrictedTraverse('@@insert-barcode')

    def _check_barcode_inserted_correctly(self):
        """ """
        self.view()
        messages = IStatusMessage(self.request).show()
        self.assertEqual(messages[-1].message, u'barcode_inserted')
        self.assertEqual(self.view.context.scan_id, '013999900000001')
        barcode_inserted = getattr(self.view.context, BARCODE_INSERTED_ATTR_ID, False)
        self.assertTrue(barcode_inserted)

    def test_barcode_inserted_in_pdf_file(self):
        """Working behavior."""
        self.assertEqual(IStatusMessage(self.request).show(), [])
        self._check_barcode_inserted_correctly()

    def test_file_must_be_pdf(self):
        view_txt = self.portal.file_txt.restrictedTraverse('@@insert-barcode')
        # nothing done and a message is added
        self.assertEqual(IStatusMessage(self.request).show(), [])
        view_txt()
        self.assertIsNone(view_txt.context.scan_id)
        barcode_inserted = getattr(view_txt.context, BARCODE_INSERTED_ATTR_ID, False)
        self.assertFalse(barcode_inserted)
        messages = IStatusMessage(self.request).show()
        self.assertEqual(messages[-1].message, u'barcode_file_must_be_pdf')

    def test_barcode_inserted_only_once(self):
        self._check_barcode_inserted_correctly()
        # call again
        self.view()
        messages = IStatusMessage(self.request).show()
        self.assertEqual(messages[-1].message, u'barcode_already_inserted')
