# encoding: utf-8

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from collective.iconifiedcategory.utils import get_category_object
from collective.iconifiedcategory.utils import calculate_category_id
from collective.zamqp.consumer import Consumer
from imio.zamqp.core import base
from imio.zamqp.core.consumer import commit
from imio.zamqp.core.consumer import DMSMainFile
from imio.zamqp.pm import interfaces
from plone import api

import logging
logger = logging.getLogger('imio.zamqp.pm')


class IconifiedAnnexConsumer(base.DMSConsumer, Consumer):
    connection_id = 'dms.connection'
    exchange = 'dms.deliberation'
    marker = interfaces.IIconifiedAnnex
    queuename = 'dms.deliberation.{0}'

IconifiedAnnexConsumerUtility = IconifiedAnnexConsumer()


def consumeIconifiedAnnex(message, event):
    doc = IconifiedAnnex('', '', message)
    doc.create_or_update()
    commit()
    message.ack()


class IconifiedAnnex(DMSMainFile):

    @property
    def file_portal_type(self):
        return ['annex', 'annexDecision']

    def _manage_after_scan_change_annex_type_to(self, the_file):
        """ """
        annex_type = get_category_object(the_file, the_file.content_category)
        after_scan_change_annex_type_to = annex_type.after_scan_change_annex_type_to
        # can not query on 'None'
        if not after_scan_change_annex_type_to:
            return

        brains = api.content.find(UID=annex_type.after_scan_change_annex_type_to)
        if not brains:
            return
        to_annex_type = brains[0].getObject()
        the_file.content_category = calculate_category_id(to_annex_type)

    def update(self, the_file, obj_file):
        """ """
        setattr(the_file, 'file', obj_file)
        # right, get the_file content_category object and check after_scan_change_annex_type_to
        self._manage_after_scan_change_annex_type_to(the_file)
        # an updated annex is de facto considered as a signed version
        the_file.to_sign = True
        the_file.signed = True
        notify(ObjectModifiedEvent(the_file))
        logger.info("File with scan_id \"{0}\" was updated!".format(self.scan_fields['scan_id']))

    def create(self, obj_file):
        """ """
        logger.info("File not created because this WS only manage file update "
                    "and we did not find an annex with scan_id \"{0}\"!".format(self.scan_fields['scan_id']))
        return
