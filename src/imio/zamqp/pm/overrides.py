# -*- coding: utf-8 -*-

from zope.i18n import translate
from imio.annex.adapters import AnnexPrettyLinkAdapter
from imio.zamqp.pm import BARCODE_ATTR_ID


class IZPMAnnexPrettyLinkAdapter(AnnexPrettyLinkAdapter):
    """ """

    def _leadingIcons(self):
        """
          Manage icons to display before the annex title.
        """
        res = super(IZPMAnnexPrettyLinkAdapter, self)._leadingIcons()
        # display a 'barcode' icon if barcode is inserted in the file
        if getattr(self.context, BARCODE_ATTR_ID, False):
            res.append(('++resource++imio.zamqp.pm/barcode.png',
                        translate('icon_help_barcode_inserted',
                                  domain="imio.zamqp.pm",
                                  context=self.request)))
        return res
