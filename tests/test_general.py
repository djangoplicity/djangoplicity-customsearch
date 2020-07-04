from django.test import TestCase, Client
from djangoplicity.customsearch.models import CustomSearchGroup, CustomSearchModel, CustomSearchField, \
    CustomSearchLayout, CustomSearchLayoutField, CustomSearch, CustomSearchCondition, CustomSearchOrdering, MATCH_TYPE
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from test_project.models import Entry, Author


def create_custom_search_model(name, model):
    return CustomSearchModel.objects.create(
        name=name,
        model=ContentType.objects.get_for_model(model)
    )


def create_custom_search_field(model, name, selector='', enable_layout=True, enable_search=True):
    return CustomSearchField.objects.create(
        model=model,
        name=name,
        field_name=name,
        selector=selector,
        enable_layout=enable_layout,
        enable_search=enable_search
    )


def create_custom_search_group(name):
    return CustomSearchGroup.objects.create(
        name=name,
    )


def create_custom_search_condition(search, field, value, match):
    return CustomSearchCondition.objects.create(
        search=search,
        field=field,
        value=value,
        match=MATCH_TYPE[match][0],
    )


def create_custom_search_layout(name, model):
    return CustomSearchLayout.objects.create(
        model=model,
        name=name
    )


def create_custom_search_layout_field(layout, field, position=None):
    return CustomSearchLayoutField.objects.create(
        layout=layout,
        field=field,
        position=position
    )


def create_custom_search(model, group, layout):
    return CustomSearch.objects.create(
        name=model.name,
        model=model,
        group=group,
        layout=layout
    )


class TestModels(TestCase):
    def setUp(self):
        self.csm = create_custom_search_model(name='Entry Custom Search Model', model=Entry)

        self.csf = create_custom_search_field(
            model=self.csm,
            name='title'
        )

        self.csg = create_custom_search_group(name='Custom Search Group')

        self.csl = create_custom_search_layout(
            model=self.csm,
            name=self.csm.name
        )

        self.cslf = create_custom_search_layout_field(
            layout=self.csl,
            field=self.csf
        )

        self.cs = create_custom_search(
            model=self.csm,
            group=self.csg,
            layout=self.csl
        )

    def test_custom_search_group_str(self):
        self.assertEqual(str(self.csg), self.csg.name)

    def test_custom_search_model_str(self):
        self.assertEqual(str(self.csm), self.csm.name)

    def test_custom_search_field_str(self):
        self.assertEqual(str(self.csf), "%s: %s" % (self.csm.name, self.csf.name))

    def test_custom_search_layout_str(self):
        self.assertEqual(str(self.csl), "%s: %s" % (self.csl.model.name, self.csl.name))

    def test_custom_search_str(self):
        self.assertEqual(str(self.cs), "%s" % self.cs.name)

    def test_custom_search_generates_human_readable_text(self):
        # without any condition
        self.assertEqual(self.cs.human_readable_text(), 'Include all entrys.')

        # adding that condition where title starts with 'This'
        create_custom_search_condition(
            search=self.cs,
            field=self.csf,
            value='This',
            match=1,
        )

        self.assertEqual(self.cs.human_readable_text(), 'Include entrys where title contains "This".')

        # adding body field
        field = create_custom_search_field(
            model=self.csm,
            name='body'
        )

        # adding that condition where body contains 'Lorem'
        create_custom_search_condition(
            search=self.cs,
            field=field,
            value='Lorem',
            match=2,
        )

        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where title contains "This" and, body starts with "Lorem".')

    def test_custom_search_returns_empty_queryset(self):
        self.assertFalse(self.cs.get_empty_queryset().exists())

    # TODO: refactor tests for ordering
    def test_custom_search__ordering(self):
        queryset = CustomSearch.objects.all()

        self.assertEqual(queryset[0], self.cs)

    def test_custom_search_field_clean_raises_validation_error(self):
        field = create_custom_search_field(
            model=self.csm,
            name='body',
            selector='something else'
        )
        with self.assertRaises(ValidationError) as context:
            field.clean()

        self.assertTrue('Selector must start with two underscores' in context.exception)

    def test_custom_search_field_is_sortable(self):
        self.assertTrue(self.csf.sortable())

    def test_custom_search_field_ordering(self):
        queryset = CustomSearchField.objects.all()
        field = create_custom_search_field(
            model=self.csm,
            name='body'
        )

        self.assertEqual(queryset[0], field)
        self.assertEqual(queryset[1], self.csf)

    def test_custom_search_condition_clean_raises_validation_error_if_field_do_not_allow_search(self):
        # when the field doesn't allow search
        field = create_custom_search_field(
            model=self.csm,
            name='body',
            enable_search=False
        )

        condition = create_custom_search_condition(
            search=self.cs,
            field=field,
            value='Lorem',
            match=2,
        )
        with self.assertRaises(ValidationError) as context:
            condition.clean()
        self.assertTrue(('Field %s does not allow searching' % field) in context.exception)

    def test_custom_search_condition_clean_raises_validation_error_if_model_do_not_match(self):
        # when the search model and the field model don't match
        model = create_custom_search_model(name='another model', model=Author)
        field = create_custom_search_field(
            model=model,
            name='first_name',
            enable_search=True
        )
        condition = create_custom_search_condition(
            search=self.cs,
            field=field,
            value='Lorem',
            match=2,
        )
        with self.assertRaises(ValidationError) as context:
            condition.clean()
        self.assertTrue(('Field %s does not belong to %s' % (field, self.cs.model.name)) in context.exception)

    def test_custom_search_layout_field_clean_raises_validation_error_if_model_do_not_match(self):
        model = create_custom_search_model(name='another model', model=Author)
        field = create_custom_search_field(
            model=self.csm,
            name='body',
            selector='something else',
            enable_layout=False
        )
        layout = create_custom_search_layout(name=model.name, model=model)
        layout_field = create_custom_search_layout_field(
            layout=layout,
            field=field,
        )
        with self.assertRaises(ValidationError) as context:
            layout_field.clean()
        self.assertTrue(('Field %s does not belong to %s' % (field, layout.model.name)) in context.exception)

    def test_custom_search_layout_field_clean_raises_validation_error_if_layout_disabled(self):
        field = create_custom_search_field(
            model=self.csm,
            name='body',
            selector='something else',
            enable_layout=False
        )
        layout_field = create_custom_search_layout_field(
            layout=self.csl,
            field=field,
        )
        with self.assertRaises(ValidationError) as context:
            layout_field.clean()
        self.assertTrue(('Field %s does not allow use in layout' % field) in context.exception)

    def test_custom_search_layout_field_ordering(self):
        field = create_custom_search_field(
            model=self.csm,
            name='body',
            selector='something else',
            enable_layout=False
        )
        layout_field1 = create_custom_search_layout_field(layout=self.csl, field=self.csf, position=0)
        layout_field2 = create_custom_search_layout_field(layout=self.csl, field=field, position=1)

        queryset = CustomSearchLayoutField.objects.all()
        self.assertEqual(queryset[0], layout_field1)
        self.assertEqual(queryset[1], layout_field2)
        self.assertEqual(queryset[2], self.cslf)
