# encoding: utf-8

import cPickle
from collective.zamqp.consumer import Consumer
from imio.zamqp.core import base
from imio.zamqp.core.consumer import commit
from imio.zamqp.core.consumer import DMSMainFile
from imio.zamqp.core.consumer import log
from imio.zamqp.pm import interfaces
from plone import api
from plone.app.blob.tests.utils import makeFileUpload
from Products.PloneMeeting.interfaces import IAnnexable
from zope.i18n import translate


class IconifiedAnnexConsumer(base.DMSConsumer, Consumer):
    connection_id = 'dms.connection'
    exchange = 'dms.deliberation'
    marker = interfaces.IIconifiedAnnex
    queuename = 'dms.deliberation.{0}'

IconifiedAnnexConsumerUtility = IconifiedAnnexConsumer()


def consumeIconifiedAnnex(message, event):
    # find the item using the 'scan_id' given in message
    scan_id = base.MessageAdapter(cPickle.loads(message.body)).metadata['scan_id']
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(meta_type='MeetingItem', scan_id=scan_id)
    item = None
    if brains:
        item = brains[0].getObject()
        annex = IconifiedAnnex(item.getPhysicalPath(), '', message)
        annex.create_or_update()
    else:
        log.warn("Could not find an item with scan_id '{0}'".format(scan_id))
    commit()
    message.ack()


class IconifiedAnnex(DMSMainFile):

    @property
    def file_portal_type(self):
        return 'MeetingFile'

    @property
    def obj_file(self):
        """We receive a NamedBlobFile, we can not handle it
           until we are in dexterity use a FileUpload instance."""
        return makeFileUpload(self.file_content, self.obj.filename)

    def _upload_file(self, item, obj_file):
        new_file = IAnnexable(item).addAnnex(
            idCandidate='scanned-signed-deliberation',
            annex_title=translate('Scanned signed deliberation',
                                  domain='imio.zamqp.pm',
                                  context=item.REQUEST),
            annex_file=obj_file,
            relatedTo='item_decision',
            meetingFileTypeUID=self.defaultDecisionFileType['meetingFileTypeObjectUID'])
        return new_file

    @property
    def defaultDecisionFileType(self):
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.folder)
        decisionFileTypes = cfg.getFileTypes(relatedTo='item_decision')
        if not decisionFileTypes:
            raise Exception("Not able find a default annex decision type!!!")
        return decisionFileTypes[0]

    def create(self, obj_file):
        annex = self._upload_file(self.folder, self.obj_file)
        annex.scan_id = self.scan_fields.get('scan_id')
        annex.reindexObject(idxs=['scan_id'])
        log.info('file has been created (scan_id: {0})'.format(annex.scan_id))
