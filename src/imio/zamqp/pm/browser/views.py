# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2017 by Imio.be
#
# GNU General Public License (GPL)
#

from pyPdf.utils import PdfReadError

from zope.i18n import translate

from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five import BrowserView
from plone import api

from plone.namedfile.file import NamedBlobFile
from plone.rfc822.interfaces import IPrimaryFieldInfo

from imio.helpers.pdf import BarcodeStamp
from imio.zamqp.core.utils import next_scan_id
from Products.PloneMeeting.config import BARCODE_INSERTED_ATTR_ID
from imio.zamqp.pm.interfaces import IImioZamqpPMSettings


class InsertBarcodeView(BrowserView):
    """ """

    def __call__(self, x=None, y=None, scale=None, force=False):
        """ """
        plone_utils = api.portal.get_tool('plone_utils')
        barcode_inserted = getattr(self.context, BARCODE_INSERTED_ATTR_ID, False)
        # barcode already inserted?
        if barcode_inserted and not force:
            msg = translate('barcode_already_inserted',
                            domain='imio.zamqp.pm',
                            context=self.request,
                            default="Barcode already inserted!")
            plone_utils.addPortalMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.request['HTTP_REFERER'])

        # file format must be PDF
        file_field_name = IPrimaryFieldInfo(self.context).fieldname
        file_obj = getattr(self.context, file_field_name)
        if not file_obj.contentType == 'application/pdf':
            msg = translate('barcode_file_must_be_pdf',
                            domain='imio.zamqp.pm',
                            context=self.request,
                            default="Barcode can only be inserted in a PDF file!")
            plone_utils.addPortalMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.request['HTTP_REFERER'])

        # still not inserted (or force insert) and file is a PDF, proceed...
        # manage x, y and scale if it is None, get it from registry
        if not x:
            x = api.portal.get_registry_record(
                'insert_barcode_x_value',
                interface=IImioZamqpPMSettings)
        if not y:
            y = api.portal.get_registry_record(
                'insert_barcode_y_value',
                interface=IImioZamqpPMSettings)
        if not scale:
            scale = api.portal.get_registry_record(
                'insert_barcode_scale_value',
                interface=IImioZamqpPMSettings)

        # if we do not check 'readers', the blob._p_blob_committed is sometimes None...
        file_obj._blob.readers
        # _p_blob_uncommitted is necessary especially for tests...
        filepath = file_obj._blob._p_blob_committed or file_obj._blob._p_blob_uncommitted
        # get scan_id, or compute and store scan_id
        scan_id = self.context.scan_id
        if not scan_id:
            scan_id = next_scan_id(file_portal_types=['annex', 'annexDecision'],
                                   cliend_id_var='client_id', scan_type='3')
        # generate barcode value
        scan_id_barcode = 'IMIO{0}'.format(scan_id)
        barcode_stamp = BarcodeStamp(filepath, barcode_value=scan_id_barcode, x=x, y=y, scale=scale)
        try:
            patched_file = barcode_stamp.stamp()
        except PdfReadError:
            msg = translate('barcode_insert_error',
                            domain='imio.zamqp.pm',
                            context=self.request,
                            default="An error occured while inserting the barcode into "
                            "the PDF file, please check the file!")
            plone_utils.addPortalMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.request['HTTP_REFERER'])
        patched_file.seek(0)
        data = patched_file.read()
        patched_file.close()
        setattr(
            self.context,
            file_field_name,
            NamedBlobFile(data,
                          filename=self.context.file.filename))

        # success
        self.context.scan_id = scan_id
        setattr(self.context, BARCODE_INSERTED_ATTR_ID, True)
        msg = translate('barcode_inserted',
                        domain='imio.zamqp.pm',
                        context=self.request,
                        default="Barcode inserted successfully!")
        # notify modified and return
        self.context.notifyModified()
        self.context.reindexObject()
        plone_utils.addPortalMessage(msg)
        return self.request.RESPONSE.redirect(self.request['HTTP_REFERER'])

    def may_insert_barcode(self):
        """ """
        member = api.user.get_current()
        # bypass for 'Manager'
        if 'Manager' in member.getRoles():
            return True

        barcode_inserted = getattr(self.context, BARCODE_INSERTED_ATTR_ID, False)
        if barcode_inserted or not member.has_permission(ModifyPortalContent, self.context):
            return False
        return True
