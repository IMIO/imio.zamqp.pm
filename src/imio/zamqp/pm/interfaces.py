# encoding: utf-8

from imio.zamqp.pm import _
from zope import schema
from zope.interface import Interface


class IIconifiedAnnex(Interface):
    """Marker interface for iconified annexes"""


class IImioZamqpPMSettings(Interface):

    insert_barcode_x_value = schema.Int(
        title=_(u'Value of x when inserting barcode into a PDF file.'),
        default=185,
    )

    insert_barcode_y_value = schema.Int(
        title=_(u'Value of y when inserting barcode into a PDF file.'),
        default=15,
    )

    insert_barcode_scale_value = schema.Int(
        title=_(u'Value of scale when inserting barcode into a PDF file.'),
        default=4,
    )

    version_when_barcode_inserted = schema.Bool(
        title=_(u'Save a version of the annex when inserting the barcode.'),
        default=False,
    )

    version_when_scanned_file_reinjected = schema.Bool(
        title=_(u'Save a version of the annex when reinjecting the scanned file.'),
        default=False,
    )
