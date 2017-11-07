# -*- coding: utf-8 -*-

from zope.i18n import translate
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from collective.iconifiedcategory.content.category import CategorySchemaPolicy
from collective.iconifiedcategory.content.categorygroup import ICategoryGroup
from collective.iconifiedcategory.content.subcategory import SubcategorySchemaPolicy
from imio.annex.adapters import AnnexPrettyLinkAdapter
from imio.zamqp.pm.interfaces import ICategoryZamqp
from imio.zamqp.pm.interfaces import ISubcategoryZamqp
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.PloneMeeting.config import BARCODE_INSERTED_ATTR_ID


class IZPMAnnexPrettyLinkAdapter(AnnexPrettyLinkAdapter):
    """ """

    def _leadingIcons(self):
        """
          Manage icons to display before the annex title.
        """
        res = super(IZPMAnnexPrettyLinkAdapter, self)._leadingIcons()
        # display a 'barcode' icon if barcode is inserted in the file
        if getattr(self.context, BARCODE_INSERTED_ATTR_ID, False):
            res.append(('++resource++imio.zamqp.pm/barcode.png',
                        translate('icon_help_barcode_inserted',
                                  domain="imio.zamqp.pm",
                                  context=self.request)))
        return res


class AfterScanChangeAnnexTypeToVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        if ICategoryGroup.providedBy(context):
            category_group = context
        else:
            category_group = context.get_category_group()
        categories = category_group.objectValues()
        for category in categories:
            category_uid = category.UID()
            category_title = category.Title()
            terms.append(SimpleVocabulary.createTerm(
                category_uid,
                category_uid,
                category_title,
            ))
            subcategories = api.content.find(
                context=category,
                object_provides='collective.iconifiedcategory.content.subcategory.ISubcategory',
                enabled=True,
            )
            for subcategory in subcategories:
                subcategory_uid = subcategory.UID
                terms.append(SimpleVocabulary.createTerm(
                    '{0}_{1}'.format(category_uid, subcategory_uid),
                    '{0}_{1}'.format(category_uid, subcategory_uid),
                    u'{0} → {1}'.format(safe_unicode(category_title), safe_unicode(subcategory.Title)),
                ))
        return SimpleVocabulary(terms)


class CategoryZamqpSchemaPolicy(CategorySchemaPolicy):

    def bases(self, schema_name, tree):
        return (ICategoryZamqp, )


class SubcategoryZamqpSchemaPolicy(SubcategorySchemaPolicy):

    def bases(self, schema_name, tree):
        return (ISubcategoryZamqp, )
