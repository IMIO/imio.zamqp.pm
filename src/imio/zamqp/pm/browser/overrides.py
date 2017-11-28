# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2016 by Imio.be
#
# GNU General Public License (GPL)
#

from imio.zamqp.core import utils as zamqp_utils
from Products.PloneMeeting.browser.overrides import PMDocumentGenerationView


class AMQPPMDocumentGenerationView(PMDocumentGenerationView):
    """Redefine the DocumentGenerationView to extend context available in the template
       and to handle POD templates sent to mailing lists."""

    def get_base_generation_context(self):
        """ """
        specific_context = super(AMQPPMDocumentGenerationView, self).get_base_generation_context()
        helper_view = self.get_generation_context_helper()
        specific_context['zamqp_utils'] = zamqp_utils
        specific_context['scan_id'] = helper_view.get_scan_id()
        return specific_context
