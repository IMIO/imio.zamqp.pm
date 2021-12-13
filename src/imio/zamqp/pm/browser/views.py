# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2017 by Imio.be
#
# GNU General Public License (GPL)
#

from imio.helpers.pdf import BarcodeStamp
from imio.zamqp.pm.interfaces import IImioZamqpPMSettings
from imio.zamqp.pm.utils import next_scan_id_pm
from plone import api
from plone.namedfile.file import NamedBlobFile
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.Five import BrowserView
from Products.PloneMeeting.config import BARCODE_INSERTED_ATTR_ID
from Products.PloneMeeting.utils import notifyModifiedAndReindex
from Products.PloneMeeting.utils import version_object
from PyPDF2.utils import PdfReadError
from zope.i18n import translate


class InsertBarcodeView(BrowserView):
    """ """

    def __init__(self, context, request):
        super(InsertBarcodeView, self).__init__(context, request)
        self.tool = api.portal.get_tool('portal_plonemeeting')

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
            scan_id = next_scan_id_pm()

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

        # versionate file before barcode is inserted if relevant
        if api.portal.get_registry_record(
                'version_when_barcode_inserted', interface=IImioZamqpPMSettings):
            version_object(
                self.context,
                comment='Versioned before barcode is inserted into the file.')

        # insert barcode
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

        # update modificationDate, it is used for caching and co
        notifyModifiedAndReindex(self.context, extra_idxs=['scan_id'])
        plone_utils.addPortalMessage(msg)
        return self.request.RESPONSE.redirect(self.request['HTTP_REFERER'])

    def may_insert_barcode(self):
        """By default, must be (Meeting)Manager to include barcode and
           barcode must not be already inserted."""
        res = False
        if self.tool.getEnableScanDocs():
            # bypass for 'Manager'
            if self.tool.isManager(self.tool, realManagers=True):
                res = True
            else:
                cfg = self.tool.getMeetingConfig(self.context)
                isManager = self.tool.isManager(cfg)
                barcode_inserted = getattr(self.context, BARCODE_INSERTED_ATTR_ID, False)
                if isManager and \
                   not barcode_inserted and \
                   _checkPermission(ModifyPortalContent, self.context):
                    res = True
        return res
