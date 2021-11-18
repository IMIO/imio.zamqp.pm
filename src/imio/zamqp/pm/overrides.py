# -*- coding: utf-8 -*-

from collective.iconifiedcategory.content.category import CategorySchemaPolicy
from collective.iconifiedcategory.content.categorygroup import ICategoryGroup
from collective.iconifiedcategory.content.subcategory import SubcategorySchemaPolicy
from imio.helpers.content import find
from imio.zamqp.pm.interfaces import ICategoryZamqp
from imio.zamqp.pm.interfaces import ISubcategoryZamqp
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.PloneMeeting.adapters import PMAnnexPrettyLinkAdapter
from Products.PloneMeeting.config import BARCODE_INSERTED_ATTR_ID
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class IZPMAnnexPrettyLinkAdapter(PMAnnexPrettyLinkAdapter):
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
        category_groups = [category_group]
        # for annexes added to item, it can be turned to an item_annex or
        # an item_decision_annex and the other way round
        if category_group.getId() == 'item_annexes':
            category_groups.append(category_group.aq_parent.get('item_decision_annexes'))
        elif category_group.getId() == 'item_decision_annexes':
            category_groups.append(category_group.aq_parent.get('item_annexes'))

        for cat_group in category_groups:
            category_group_title = cat_group.Title()
            categories = cat_group.objectValues()

            for category in categories:
                category_uid = category.UID()
                # display content_category_group title in the term title
                category_title = u'{0} → {1}'.format(
                    safe_unicode(category_group_title),
                    safe_unicode(category.Title()))
                terms.append(SimpleVocabulary.createTerm(
                    category_uid,
                    category_uid,
                    category_title,
                ))
                subcategories = find(
                    context=category,
                    object_provides='collective.iconifiedcategory.content.subcategory.ISubcategory',
                    enabled=True,
                    unrestricted=True
                )
                for subcategory in subcategories:
                    subcategory_uid = subcategory.UID
                    terms.append(SimpleVocabulary.createTerm(
                        '{0}_{1}'.format(category_uid, subcategory_uid),
                        '{0}_{1}'.format(category_uid, subcategory_uid),
                        u'{0} → {1}'.format(
                            safe_unicode(category_title),
                            safe_unicode(subcategory.Title)),
                    ))
        return SimpleVocabulary(terms)


class CategoryZamqpSchemaPolicy(CategorySchemaPolicy):

    def bases(self, schema_name, tree):
        return (ICategoryZamqp, )


class SubcategoryZamqpSchemaPolicy(SubcategorySchemaPolicy):

    def bases(self, schema_name, tree):
        return (ISubcategoryZamqp, )
