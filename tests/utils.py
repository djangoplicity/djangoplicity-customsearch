from django.contrib.contenttypes.models import ContentType

from djangoplicity.customsearch.models import (
    CustomSearchGroup, CustomSearchModel, CustomSearchField,
    CustomSearchLayout, CustomSearchLayoutField, CustomSearch,
    CustomSearchCondition, CustomSearchOrdering, MATCH_TYPE
)


def create_custom_search_model(name, model):
    return CustomSearchModel.objects.create(name=name, model=ContentType.objects.get_for_model(model))


def create_custom_search_field(model, name, selector='', enable_layout=True, enable_search=True, sort_selector=''):
    return CustomSearchField.objects.create(
        model=model,
        name=name,
        field_name=name,
        selector=selector,
        enable_layout=enable_layout,
        enable_search=enable_search,
        sort_selector=sort_selector
    )


def create_custom_search_group(name):
    return CustomSearchGroup.objects.create(name=name)


def create_custom_search_condition(search, field, value, match, exclude=False, and_together=False):
    return CustomSearchCondition.objects.create(
        search=search,
        field=field,
        value=value,
        match=MATCH_TYPE[match][0],
        exclude=exclude,
        and_together=and_together
    )


def create_custom_search_ordering(search, field, descending=False):
    return CustomSearchOrdering.objects.create(search=search, field=field, descending=descending)


def create_custom_search_layout(name, model):
    return CustomSearchLayout.objects.create(model=model, name=name)


def create_custom_search_layout_field(layout, field, position=None):
    return CustomSearchLayoutField.objects.create(layout=layout, field=field, position=position)


def create_custom_search(model, group, layout):
    return CustomSearch.objects.create(name=model.name, model=model, group=group, layout=layout)
