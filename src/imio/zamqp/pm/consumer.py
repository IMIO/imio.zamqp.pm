# encoding: utf-8

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from collective.zamqp.consumer import Consumer
from imio.zamqp.core import base
from imio.zamqp.core.consumer import commit
from imio.zamqp.core.consumer import DMSMainFile
from imio.zamqp.pm import interfaces

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

    def update(self, the_file, obj_file):
        """ """
        setattr(the_file, 'file', obj_file)
        # an updated annex is de facto considered as a signed version
        the_file.to_sign = True
        the_file.signed = True
        notify(ObjectModifiedEvent(the_file))

    def create(self, obj_file):
        """ """
        logger.info("File not created because this WS only manage file update "
                    "and we did not find an annex with scan_id \"{0}\"!".format(self.scan_fields['scan_id']))
        return
