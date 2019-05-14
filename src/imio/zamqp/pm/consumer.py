# encoding: utf-8

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from collective.iconifiedcategory.utils import get_category_object
from collective.iconifiedcategory.utils import calculate_category_id
from collective.zamqp.consumer import Consumer
from imio.zamqp.core import base
from imio.zamqp.core.consumer import consume
from imio.zamqp.core.consumer import DMSMainFile
from imio.zamqp.pm import interfaces
from Products.PloneMeeting.utils import version_object

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
    consume(IconifiedAnnex, '', '', message)


class IconifiedAnnex(DMSMainFile):
    """ """

    @property
    def file_portal_types(self):
        return ['annex', 'annexDecision']

    def _manage_after_scan_change_annex_type_to(self, the_file):
        """Change annex annex_type if defined in annex_type.after_scan_change_annex_type_to."""
        old_annex_type = get_category_object(the_file, the_file.content_category)
        after_scan_change_annex_type_to = old_annex_type.after_scan_change_annex_type_to
        # can not query on 'None'
        if not after_scan_change_annex_type_to:
            return

        brains = api.content.find(UID=old_annex_type.after_scan_change_annex_type_to)
        if not brains:
            return
        to_annex_type = brains[0].getObject()
        the_file.content_category = calculate_category_id(to_annex_type)

        # for items, the annex_type can move from item_annex type to item_decision_annex type
        # and the other way round, in this case, the annex portal_type changed
        if the_file.aq_parent.portal_type.startswith('MeetingItem'):
            old_annex_type_group = old_annex_type.get_category_group()
            to_annex_type_group = to_annex_type.get_category_group()
            if old_annex_type_group != to_annex_type_group:
                new_portal_type = 'annex'
                if to_annex_type_group.getId() == 'item_decision_annexes':
                    new_portal_type = 'annexDecision'
                the_file.portal_type = new_portal_type

    def update(self, the_file, obj_file):
        """ """
        # versionate annex before the scanned file is reinjected
        if api.portal.get_registry_record(
                'version_when_scanned_file_reinjected',
                interface=interfaces.IImioZamqpPMSettings):
            version_object(
                the_file,
                only_once=True,
                comment='Versioned before scanned file was reinjected.')

        setattr(the_file, 'file', obj_file)
        # right, get the_file content_category object and check after_scan_change_annex_type_to
        self._manage_after_scan_change_annex_type_to(the_file)
        # an updated annex is de facto considered as a signed version
        the_file.to_sign = True
        the_file.signed = True
        # update scan attributes like 'pages_number', 'scan_date', ...
        self.set_scan_attr(the_file)
        notify(ObjectModifiedEvent(the_file))
        logger.info("File at \"{0}\" with scan_id \"{1}\" was updated!".format(
            "/".join(the_file.getPhysicalPath()),
            self.scan_fields['scan_id']))

    def create(self, obj_file):
        """ """
        logger.info("File not created because this WS only manage file update "
                    "and we did not find an annex with scan_id \"{0}\"!".format(self.scan_fields['scan_id']))
        return
