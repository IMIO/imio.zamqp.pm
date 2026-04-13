# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from AccessControl import Unauthorized
from collective.eeafaceted.batchactions import _
from collective.eeafaceted.batchactions.browser.views import BaseBatchActionForm
from imio.actionspanel.interfaces import IContentDeletable
from imio.helpers.pdf import BarcodeStamp
from imio.zamqp.pm.interfaces import IImioZamqpPMSettings
from imio.zamqp.pm.utils import next_scan_id_pm
from plone import api
from plone.namedfile.file import NamedBlobFile
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.PloneMeeting.utils import is_proposing_group_editor
from Products.PloneMeeting.utils import notifyModifiedAndReindex
from Products.PloneMeeting.utils import version_object
from PyPDF2.utils import PdfReadError
from zope.i18n import translate


class InsertBarcodeView(BrowserView):
    """ """

    def __init__(self, context, request):
        super(InsertBarcodeView, self).__init__(context, request)
        self.tool = api.portal.get_tool('portal_plonemeeting')

    def __call__(self, x=None, y=None, scale=None, force=False, redirect=True):
        """ """
        if not self.may_insert_barcode():
            raise Unauthorized
        plone_utils = api.portal.get_tool('plone_utils')
        # barcode already inserted?
        if self.context.scan_id and not force:
            if not redirect:
                return False
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
            if not redirect:
                return False
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
            if not redirect:
                return False
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
            NamedBlobFile(data, filename=self.context.file.filename))

        # success
        self.context.scan_id = scan_id
        # update modificationDate, it is used for caching and co
        notifyModifiedAndReindex(self.context, extra_idxs=['scan_id'])

        if not redirect:
            return True
        msg = translate('barcode_inserted',
                        domain='imio.zamqp.pm',
                        context=self.request,
                        default="Barcode inserted successfully!")
        plone_utils.addPortalMessage(msg)
        return self.request.RESPONSE.redirect(self.request['HTTP_REFERER'])

    def may_insert_barcode(self):
        """By default, must be (Meeting)Manager to include barcode and
           barcode must not be already inserted.
           But if user can insert barcode and annex editable or
           annexDecision deletable, it can also insert a barcode."""
        res = False
        if self.tool.getEnableScanDocs():
            cfg = self.tool.getMeetingConfig(self.context)
            if (self.tool.isManager(cfg) or cfg.getAnnexEditorMayInsertBarcode()) and \
               not self.context.scan_id and \
               (_checkPermission(ModifyPortalContent, self.context)
                    or (self.context.portal_type == 'annexDecision' and
                        cfg.getOwnerMayDeleteAnnexDecision() and
                        IContentDeletable(self.context)._may_delete_decision_annex(
                            self.context.aq_parent))):
                res = True
        return res


class InsertBarcodeBatchActionForm(BaseBatchActionForm):

    label = _("insert-barcode-batch-action-but")
    button_with_icon = True
    section = "annexes"

    def __init__(self, context, request):
        super(InsertBarcodeBatchActionForm, self).__init__(
            context, request)
        self.tool = api.portal.get_tool('portal_plonemeeting')
        self.cfg = self.tool.getMeetingConfig(context)

    def available(self):
        """ """
        res = False
        if "insert-barcode" in self.cfg.getEnabledAnnexesBatchActions():
            if self.tool.isManager(self.cfg):
                return True
            meta_type = self.context.getTagName()
            if meta_type == "MeetingItem" and \
               is_proposing_group_editor(self.context.getProposingGroup(), self.cfg):
                res = True
            elif meta_type == "MeetingAdvice" and _checkPermission(ModifyPortalContent, self.context):
                res = True
        return res

    def _apply(self, **data):
        """ """
        success = []
        failed = []
        for brain in self.brains:
            obj = brain.getObject()
            insert_barcode_view = obj.restrictedTraverse('insert-barcode')
            if insert_barcode_view.may_insert_barcode():
                res = insert_barcode_view(redirect=False)
                if res:
                    success.append(u'"{0}"'.format(safe_unicode(obj.Title())))
                else:
                    failed.append(u'"{0}"'.format(safe_unicode(obj.Title())))
            else:
                failed.append(u'"{0}"'.format(safe_unicode(obj.Title())))
        if success:
            msg = translate('insert_barcode_batch_action_success',
                            domain="imio.zamqp.pm",
                            mapping={'num_success': len(success),
                                     'success': u", ".join(success)},
                            context=self.request,
                            default="Barcode was inserted in ${num_success} following annexes: ${success}.")
            api.portal.show_message(msg, request=self.request)
        if failed:
            msg = translate('insert_barcode_batch_action_failed',
                            domain="imio.zamqp.pm",
                            mapping={'num_failed': len(failed),
                                     'failed': u", ".join(failed)},
                            context=self.request,
                            default="Barcode failed to be inserted for ${num_failed} following annexes: ${failed}.")
            api.portal.show_message(msg, type='warning', request=self.request)
