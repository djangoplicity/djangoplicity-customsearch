from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase

from djangoplicity.customsearch.models import (
    CustomSearchGroup, CustomSearchModel, CustomSearchField,
    CustomSearchLayout, CustomSearchLayoutField, CustomSearch,
    CustomSearchCondition, CustomSearchOrdering, MATCH_TYPE
)
from test_project.models import Entry, Author


def create_custom_search_model(name, model):
    return CustomSearchModel.objects.create(name=name, model=ContentType.objects.get_for_model(model))


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
    return CustomSearchGroup.objects.create(name=name)


def create_custom_search_condition(search, field, value, match):
    return CustomSearchCondition.objects.create(
        search=search,
        field=field,
        value=value,
        match=MATCH_TYPE[match][0],
    )


def create_custom_search_ordering(search, field, descending=False):
    return CustomSearchOrdering.objects.create(search=search, field=field, descending=descending)


def create_custom_search_layout(name, model):
    return CustomSearchLayout.objects.create(model=model, name=name)


def create_custom_search_layout_field(layout, field, position=None):
    return CustomSearchLayoutField.objects.create(layout=layout, field=field, position=position)


def create_custom_search(model, group, layout):
    return CustomSearch.objects.create(name=model.name, model=model, group=group, layout=layout)


class TestModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.csm = create_custom_search_model(name='Entry Custom Search Model', model=Entry)

        cls.csf = create_custom_search_field(model=cls.csm, name='title')

        cls.csg = create_custom_search_group(name='Custom Search Group')

        cls.csl = create_custom_search_layout(model=cls.csm, name=cls.csm.name)

        cls.cslf = create_custom_search_layout_field(layout=cls.csl, field=cls.csf)

        cls.cs = create_custom_search(model=cls.csm, group=cls.csg, layout=cls.csl)

    def test_custom_search_group_str(self):
        """Test the custom search group string representation"""
        self.assertEqual(str(self.csg), self.csg.name)

    def test_custom_search_model_str(self):
        """Test the custom search model string representation"""
        self.assertEqual(str(self.csm), self.csm.name)

    def test_custom_search_field_str(self):
        """Test the custom search field string representation"""
        self.assertEqual(str(self.csf), "%s: %s" % (self.csm.name, self.csf.name))

    def test_custom_search_layout_str(self):
        """Test the custom search layout string representation"""
        self.assertEqual(str(self.csl), "%s: %s" % (self.csl.model.name, self.csl.name))

    def test_custom_search_str(self):
        """Test the custom search string representation"""
        self.assertEqual(str(self.cs), "%s" % self.cs.name)

    def test_custom_search_generates_human_readable_text(self):
        """Test that custom search generates human readable text"""
        # without any condition
        self.assertEqual(self.cs.human_readable_text(), 'Include all entrys.')

        # adding that condition where title starts with 'This'
        create_custom_search_condition(search=self.cs, field=self.csf, value='This', match=1)

        self.assertEqual(self.cs.human_readable_text(), 'Include entrys where title contains "This".')

        # adding body field
        field = create_custom_search_field(model=self.csm, name='body')

        # adding that condition where body contains 'Lorem'
        create_custom_search_condition(search=self.cs, field=field, value='Lorem', match=2, )

        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where title contains "This" and, body starts with "Lorem".')

    def test_custom_search_returns_empty_queryset(self):
        """Test custom search empty queryset"""
        self.assertFalse(self.cs.get_empty_queryset().exists())

    # TODO: refactor tests for ordering
    def test_custom_search_ordering(self):
        """Test that the custom search ordering is right"""
        queryset = CustomSearch.objects.all()

        self.assertEqual(queryset[0], self.cs)

    def test_custom_search_clean_raises_validation_error(self):
        """Test clean method on custom search raises a validation error when the layout does not belong to the
        model """
        model = create_custom_search_model(name='author model', model=Author)
        layout = create_custom_search_layout(name='author layout', model=model)
        search = create_custom_search(model=self.csm, group=self.csg, layout=layout)

        with self.assertRaises(ValidationError) as context:
            search.clean()
        self.assertTrue(('Layout %s does not belong to %s' % (layout, self.csm)) in context.exception)

    def test_custom_search_field_clean_raises_validation_error(self):
        """Test clean method on custom search field raises a validation error if the selector is not valid"""
        field = create_custom_search_field(model=self.csm, name='body', selector='something else')
        with self.assertRaises(ValidationError) as context:
            field.clean()

        self.assertTrue('Selector must start with two underscores' in context.exception)

    def test_custom_search_field_is_sortable(self):
        """Test that custom search field is sortable"""
        self.assertTrue(self.csf.sortable())

    def test_custom_search_field_ordering(self):
        """Test the custom search field ordering is right"""
        queryset = CustomSearchField.objects.all()
        field = create_custom_search_field(model=self.csm, name='body')

        self.assertEqual(queryset[0], field)
        self.assertEqual(queryset[1], self.csf)

    def test_custom_search_condition_clean_raises_validation_error_if_field_does_not_allow_search(self):
        """Test clean method on custom search condition raises a validation error if search is disabled in field"""
        field = create_custom_search_field(model=self.csm, name='body', enable_search=False)
        condition = create_custom_search_condition(search=self.cs, field=field, value='Lorem', match=2)

        with self.assertRaises(ValidationError) as context:
            condition.clean()
        self.assertTrue(('Field %s does not allow searching' % field) in context.exception)

    def test_custom_search_condition_clean_raises_validation_error_if_model_do_not_match(self):
        """Test clean method on custom search condition raises a validation error when the field does not belong to
        the model"""
        model = create_custom_search_model(name='author model', model=Author)
        field = create_custom_search_field(model=model, name='first_name', enable_search=True)
        condition = create_custom_search_condition(search=self.cs, field=field, value='Lorem', match=2)

        with self.assertRaises(ValidationError) as context:
            condition.clean()
        self.assertTrue(('Field %s does not belong to %s' % (field, self.cs.model.name)) in context.exception)

    def test_custom_search_condition_prepared_value(self):
        """Test prepared_value method of custom search condition returns the right value"""
        # This test is disabled because the date doesn't match, it needs to be mocked
        # condition = create_custom_search_condition(search=self.cs, field=self.csf, value='now()', match=14)
        # self.assertEqual(condition.prepared_value(), datetime.now())

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='2020', match=10)
        self.assertEqual(condition.prepared_value(), 2020)

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='false', match=18)
        self.assertEqual(condition.prepared_value(), False)

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='true', match=18)
        self.assertEqual(condition.prepared_value(), True)

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='other', match=18)
        with self.assertRaises(ValidationError) as context:
            condition.prepared_value()
        self.assertTrue('Value is not a truth value.' in context.exception)

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='contains', match=1)
        self.assertEqual(condition.prepared_value(), 'contains')

    def test_custom_search_condition_check_value(self):
        """Test check_value method of custom search condition raises ValidationError"""
        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='other', match=10)
        with self.assertRaises(ValidationError) as context:
            condition.check_value()
        self.assertTrue(("Value must be an integer for match type '%s'." % MATCH_TYPE[10][1]) in context.exception)

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='other', match=18)
        with self.assertRaises(ValidationError) as context:
            condition.check_value()
        self.assertTrue(
            ("Value must be either true or false for match type '%s'." % MATCH_TYPE[18][1]) in context.exception)

    def test_custom_search_layout_field_clean_raises_validation_error_if_model_do_not_match(self):
        """Test prepared_value method of custom search layout field raises ValidationError when the field does not belong to
        the model"""
        model = create_custom_search_model(name='author model', model=Author)
        field = create_custom_search_field(model=self.csm, name='body', selector='something else')
        layout = create_custom_search_layout(name=model.name, model=model)
        layout_field = create_custom_search_layout_field(layout=layout, field=field)

        with self.assertRaises(ValidationError) as context:
            layout_field.clean()
        self.assertTrue(('Field %s does not belong to %s' % (field, layout.model.name)) in context.exception)

    def test_custom_search_layout_field_clean_raises_validation_error_if_layout_disabled(self):
        """Test prepared_value method of custom search layout field raises ValidationError when the layout is
        disabled """
        field = create_custom_search_field(model=self.csm, name='body', selector='something else', enable_layout=False)
        layout_field = create_custom_search_layout_field(layout=self.csl, field=field)

        with self.assertRaises(ValidationError) as context:
            layout_field.clean()
        self.assertTrue(('Field %s does not allow use in layout' % field) in context.exception)

    def test_custom_search_layout_field_ordering(self):
        """Test the custom search layout field ordering is right"""
        field = create_custom_search_field(model=self.csm, name='body', selector='something else', enable_layout=False)
        layout_field1 = create_custom_search_layout_field(layout=self.csl, field=self.csf, position=0)
        layout_field2 = create_custom_search_layout_field(layout=self.csl, field=field, position=1)

        queryset = CustomSearchLayoutField.objects.all()
        self.assertEqual(queryset[0], layout_field1)
        self.assertEqual(queryset[1], layout_field2)
        self.assertEqual(queryset[2], self.cslf)

    def test_custom_search_ordering_clean_raises_validation_error_if_model_do_not_match(self):
        """Test clean method of custom search ordering field raises ValidationError when the field does not belong to
        the model"""
        model = create_custom_search_model(name='author model', model=Author)
        field = create_custom_search_field(model=model, name='body', selector='something else')
        ordering = create_custom_search_ordering(search=self.cs, field=field)

        with self.assertRaises(ValidationError) as context:
            ordering.clean()
        self.assertTrue(('Field %s does not belong to %s' % (field, self.cs.model.name)) in context.exception)

    def test_custom_search_ordering_clean_raises_validation_error_if_field_does_not_allow_search(self):
        """Test prepared_value method of custom search layout field raises ValidationError when search in field is
        disabled """
        field = create_custom_search_field(model=self.csm, name='body', enable_search=False)
        ordering = create_custom_search_ordering(search=self.cs, field=field)

        with self.assertRaises(ValidationError) as context:
            ordering.clean()
        self.assertTrue(('Field %s does not allow ordering' % field) in context.exception)
