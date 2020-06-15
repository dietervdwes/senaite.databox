# -*- coding: utf-8 -*-

from bika.lims import api
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from senaite.databox import _
from senaite.databox import logger
from senaite.databox.config import TMP_FOLDER_KEY
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IDataBoxBehavior(model.Schema):

    # N.B. do not name this field `portal_type`
    query_type = schema.Choice(
        title=_(u"Query Type"),
        description=_(u"The type to query"),
        source="senaite.databox.vocabularies.query_types",
        required=False,
    )

    columns = schema.Dict(
        title=_(u"Columns"),
        key_type=schema.Choice(
            title=_(u"Column"),
            source="senaite.databox.vocabularies.display_columns"),
        value_type=schema.Dict(
            key_type=schema.TextLine(title=u"Key"),
            value_type=schema.TextLine(title=u"Value"),
        ),
        required=False,
    )

    date_index = schema.Choice(
        title=_(u"Query date index"),
        description=_(u"The date index to query"),
        source="senaite.databox.vocabularies.date_indexes",
        required=True,
        default="created",
    )

    directives.widget("date_from", DatetimeFieldWidget, klass=u"datepicker")
    date_from = schema.Datetime(
        title=_(u"Query from date"),
        required=False,
    )

    directives.widget("date_to", DatetimeFieldWidget, klass=u"datepicker")
    date_to = schema.Datetime(
        title=_(u"Query to date"),
        required=False,
    )

    limit = schema.Int(
        title=_(u"Limit"),
        description=_(u"Limit Search Results"),
        required=False,
        default=5,
        min=1,
    )

    sort_on = schema.TextLine(
        title=_(u"label_sort_on", default=u"Sort on"),
        description=_(u"Sort the databox on this index"),
        required=False,
    )

    # form.omitted("sort_reversed")
    sort_reversed = schema.Bool(
        title=_(u"label_sort_reversed", default=u"Reversed order"),
        description=_(u"Sort the results in reversed order"),
        required=False,
    )


@implementer(IDataBoxBehavior)
@adapter(IDexterityContent)
class DataBox(object):

    def __init__(self, context):
        self.context = context
        logger.info("IDataBoxBehavior::__init__:context={}"
                    .format(repr(context)))

    def get_fields(self):
        """Returns all schema fields of the selected query type

        IMPORTANT: Do not call from within `__init__` due to permissions
        """
        obj = self._create_temporary_object()
        if obj is None:
            return []
        fields = api.get_fields(obj).values()
        return fields

    def get_catalog_indexes(self):
        """Returns available catalog indexes for the selected query type
        """
        catalog = api.get_tool(self.get_query_catalog())
        return sorted(catalog.indexes())

    def get_catalog_columns(self):
        """Returns available catalog schema columns for the selected query type
        """
        catalog = api.get_tool(self.get_query_catalog())
        return sorted(catalog.schema())

    def _create_temporary_object(self):
        """Create a temporary object to fetch the fields from

        This is needed to get schema extended fields as well.
        """
        portal_type = self.query_type
        if portal_type is None:
            return None
        portal_factory = api.get_tool("portal_factory")
        temp_folder = portal_factory._getTempFolder(TMP_FOLDER_KEY)
        if portal_type in temp_folder:
            return temp_folder[portal_type]
        temp_folder.invokeFactory(portal_type, id=portal_type)
        return temp_folder[portal_type]

    def get_query_catalog(self, default="portal_catalog"):
        """Returns the primary catalog for the selected query type

        :returns: catalog ID
        """
        archetype_tool = api.get_tool("archetype_tool")
        portal_type = self.query_type
        catalogs = archetype_tool.getCatalogsByType(portal_type)
        if len(catalogs) == 0:
            return default
        primary_catalog = catalogs[0]
        return primary_catalog.getId()

    def get_catalog_tool(self):
        """Returns the primary catalog tool for the selected query type
        """
        return api.get_tool(self.get_query_catalog())

    @property
    def sort_order(self):
        if self.sort_reversed is False:
            return "descending"
        return "ascending"

    # Getters and setters for our fields.

    # QUERY TYPE

    def _set_query_type(self, value):
        self.context.query_type = value

    def _get_query_type(self):
        return getattr(self.context, "query_type", None)

    query_type = property(_get_query_type, _set_query_type)

    # COLUMNS

    def _set_columns(self, value):
        self.context.columns = value

    def _get_columns(self):
        return getattr(self.context, "columns", {})

    columns = property(_get_columns, _set_columns)

    # DATE FROM

    def _set_date_from(self, value):
        self.context.date_from = value

    def _get_date_from(self):
        return getattr(self.context, "date_from", None)

    date_from = property(_get_date_from, _set_date_from)

    # DATE TO

    def _set_date_to(self, value):
        self.context.date_to = value

    def _get_date_to(self):
        return getattr(self.context, "date_to", None)

    date_to = property(_get_date_to, _set_date_to)

    # LIMIT

    def _set_limit(self, value):
        self.context.limit = value

    def _get_limit(self):
        return getattr(self.context, "limit", 1000)

    limit = property(_get_limit, _set_limit)

    # SORT ON

    def _set_sort_on(self, value):
        self.context.sort_on = value

    def _get_sort_on(self, default="created"):
        return getattr(self.context, "sort_on", default)

    sort_on = property(_get_sort_on, _set_sort_on)

    # SORT REVERSED

    def _set_sort_reversed(self, value):
        self.context.sort_reversed = value

    def _get_sort_reversed(self):
        return getattr(self.context, "sort_reversed", None)

    sort_reversed = property(_get_sort_reversed, _set_sort_reversed)
