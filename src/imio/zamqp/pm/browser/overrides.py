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
        specific_context['zamqp_utils'] = zamqp_utils
        return specific_context
