# encoding: utf-8

from imio.zamqp.pm import _
from zope.interface import Interface
from zope import schema


class IIconifiedAnnex(Interface):
    """Marker interface for iconified annexes"""


class IImioZamqpPMSettings(Interface):

    insert_barcode_x_value = schema.Int(
        title=_(u'Value of x when inserting barcode into a PDF file.'),
        default=50,
    )

    insert_barcode_y_value = schema.Int(
        title=_(u'Value of y when inserting barcode into a PDF file.'),
        default=50,
    )

    insert_barcode_scale_value = schema.Int(
        title=_(u'Value of scale when inserting barcode into a PDF file.'),
        default=4,
    )
