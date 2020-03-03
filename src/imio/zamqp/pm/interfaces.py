# encoding: utf-8

from collective.iconifiedcategory.content.category import ICategory
from collective.iconifiedcategory.content.subcategory import ISubcategory
from imio.zamqp.pm import _
from zope.interface import Interface
from zope import schema


class IIconifiedAnnex(Interface):
    """Marker interface for iconified annexes"""


class IAnnexTypeZamqp(Interface):
    """Specific fields when using zamqp"""

    after_scan_change_annex_type_to = schema.Choice(
        title=_(u'after_scan_change_annex_type_to_title'),
        description=_(u"after_scan_change_annex_type_to_descr"),
        vocabulary=u'imio.zamqp.pm.after_scan_change_annex_type_to_vocabulary',
        required=False,
    )


class ICategoryZamqp(ICategory, IAnnexTypeZamqp):
    """Specific fields when using zamqp"""


class ISubcategoryZamqp(ISubcategory, IAnnexTypeZamqp):
    """Specific fields when using zamqp"""


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
