from django.core.exceptions import ValidationError
from django.test import TestCase

from djangoplicity.customsearch.models import (
    CustomSearchField,
    CustomSearchLayoutField, CustomSearch,
    MATCH_TYPE
)
from test_project.models import Entry, Author
from .utils import (
    create_custom_search, create_custom_search_model,
    create_custom_search_field, create_custom_search_group,
    create_custom_search_layout_field, create_custom_search_layout, create_custom_search_condition,
    create_custom_search_ordering
)


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
        """Test that custom search generates human readable text describing the search"""
        self.assertEqual(self.cs.human_readable_text(), 'Include all entrys.')

        # adding that condition where title starts with 'This'
        create_custom_search_condition(search=self.cs, field=self.csf, value='This', match=1)
        self.assertEqual(self.cs.human_readable_text(), 'Include entrys where title contains "This".')

        # adding body field
        body = create_custom_search_field(model=self.csm, name='body')
        pub_date = create_custom_search_field(model=self.csm, name='pub_date')

        # adding condition where body is exactly 'Lorem'
        create_custom_search_condition(search=self.cs, field=body, value='Lorem', match=0, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body matches "Lorem" and, title contains "This".')

        # adding condition where body ends with 'Lorem'
        create_custom_search_condition(search=self.cs, field=body, value='Lorem', match=3, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body ends with "Lorem" or matches "Lorem" and, title contains "This".')

        # adding condition where body matches expresion [a-z]
        create_custom_search_condition(search=self.cs, field=body, value='[a-z]', match=4, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body matches "Lorem" or ends with "Lorem" or matches regular '
                         'expression "[a-z]" and, title contains "This".')

        # adding condition where body matches (case-insensitive) with 'Lorem'
        create_custom_search_condition(search=self.cs, field=body, value='Lorem', match=5, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body matches regular expression "[a-z]" or ends with "Lorem" or '
                         'matches (case-insensitive) "Lorem" or matches "Lorem" and, title contains "This".')

        # adding condition where body contains (case-insensitive) 'Lorem'
        create_custom_search_condition(search=self.cs, field=body, value='Lorem', match=6, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body matches regular expression "[a-z]" or ends with "Lorem" or '
                         'contains (case-insensitive) "Lorem" or matches (case-insensitive) "Lorem" or matches '
                         '"Lorem" and, title contains "This".')

        # adding condition where body starts (case-insensitive) with 'Lorem'
        create_custom_search_condition(search=self.cs, field=body, value='Lorem', match=7, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body starts with (case-insensitive) "Lorem" or matches regular '
                         'expression "[a-z]" or matches "Lorem" or ends with "Lorem" or contains (case-insensitive) '
                         '"Lorem" or matches (case-insensitive) "Lorem" and, title contains "This".')

        # adding condition where body ends (case-insensitive) with 'Lorem'
        create_custom_search_condition(search=self.cs, field=body, value='Lorem', match=8, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body starts with (case-insensitive) "Lorem" or ends with ('
                         'case-insensitive) "Lorem" or matches regular expression "[a-z]" or matches "Lorem" or ends '
                         'with "Lorem" or contains (case-insensitive) "Lorem" or matches (case-insensitive) "Lorem" '
                         'and, title contains "This".')

        # adding condition where body matches expresion (case-insensitive) [a-z]
        create_custom_search_condition(search=self.cs, field=body, value='[a-z]', match=9, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body starts with (case-insensitive) "Lorem" or ends with ('
                         'case-insensitive) "Lorem" or matches regular expression (case-insensitive) "[a-z]" or '
                         'matches regular expression "[a-z]" or matches "Lorem" or ends with "Lorem" or contains ('
                         'case-insensitive) "Lorem" or matches (case-insensitive) "Lorem" and, title contains "This".')

        # adding condition where pub_date year is 2020
        create_custom_search_condition(search=self.cs, field=pub_date, value='2020', match=10, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body starts with (case-insensitive) "Lorem" or ends with ('
                         'case-insensitive) "Lorem" or matches regular expression (case-insensitive) "[a-z]" or '
                         'matches regular expression "[a-z]" or matches "Lorem" or ends with "Lorem" or contains ('
                         'case-insensitive) "Lorem" or matches (case-insensitive) "Lorem" and, pub_date year is '
                         '"2020" and, title contains "This".')

        # adding condition where pub_date if after 2020
        create_custom_search_condition(search=self.cs, field=pub_date, value='2020', match=14, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body starts with (case-insensitive) "Lorem" or ends with ('
                         'case-insensitive) "Lorem" or matches regular expression (case-insensitive) "[a-z]" or '
                         'matches regular expression "[a-z]" or matches "Lorem" or ends with "Lorem" or contains ('
                         'case-insensitive) "Lorem" or matches (case-insensitive) "Lorem" and, pub_date is after '
                         '"2020" or year is "2020" and, title contains "This".')

        # adding condition where pub_date is null
        create_custom_search_condition(search=self.cs, field=pub_date, value='true', match=18, )
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body starts with (case-insensitive) "Lorem" or ends with ('
                         'case-insensitive) "Lorem" or matches regular expression (case-insensitive) "[a-z]" or '
                         'matches regular expression "[a-z]" or matches "Lorem" or ends with "Lorem" or contains ('
                         'case-insensitive) "Lorem" or matches (case-insensitive) "Lorem" and, pub_date is null or is '
                         'after "2020" or year is "2020" and, title contains "This".')

        # adding condition to exclude entries where pub_date is not null
        create_custom_search_condition(search=self.cs, field=pub_date, value='false', match=18, exclude=True,
                                       and_together=True)
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body starts with (case-insensitive) "Lorem" or ends with ('
                         'case-insensitive) "Lorem" or matches regular expression (case-insensitive) "[a-z]" or '
                         'matches regular expression "[a-z]" or matches "Lorem" or ends with "Lorem" or contains ('
                         'case-insensitive) "Lorem" or matches (case-insensitive) "Lorem" and, pub_date is null or is '
                         'after "2020" or year is "2020" and, title contains "This". Exclude entrys where pub_date is '
                         'not null.')

        # adding condition to exclude entries where pub_date contains false
        create_custom_search_condition(search=self.cs, field=pub_date, value='false', match=1,
                                       and_together=True)
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body starts with (case-insensitive) "Lorem" or ends with ('
                         'case-insensitive) "Lorem" or matches regular expression (case-insensitive) "[a-z]" or '
                         'matches regular expression "[a-z]" or matches "Lorem" or ends with "Lorem" or contains ('
                         'case-insensitive) "Lorem" or matches (case-insensitive) "Lorem" and, pub_date is null or '
                         'contains "false" or is after "2020" or year is "2020" and, title contains "This". Exclude '
                         'entrys where pub_date is not null.')

        # adding condition to order the results by title
        create_custom_search_ordering(self.cs, field=self.csf, descending=True)
        self.assertEqual(self.cs.human_readable_text(),
                         'Include entrys where body starts with (case-insensitive) "Lorem" or ends with ('
                         'case-insensitive) "Lorem" or matches regular expression (case-insensitive) "[a-z]" or '
                         'matches regular expression "[a-z]" or matches "Lorem" or ends with "Lorem" or contains ('
                         'case-insensitive) "Lorem" or matches (case-insensitive) "Lorem" and, pub_date is null or '
                         'contains "false" or is after "2020" or year is "2020" and, title contains "This". Exclude '
                         'entrys where pub_date is not null. Order result by title.')

    def test_custom_search_returns_empty_queryset(self):
        """Test custom search empty queryset"""
        self.assertFalse(self.cs.get_empty_queryset().exists())

    def test_custom_search_ordering(self):
        """Test that the custom search ordering is correct"""
        model = create_custom_search_model(name='Author Custom Search Model', model=Author)
        group = create_custom_search_group(name='Custom Search Group')
        layout = create_custom_search_layout(model=model, name=model.name)
        search = create_custom_search(model=model, group=group, layout=layout)

        queryset = CustomSearch.objects.all()

        self.assertEqual(queryset[0], search)
        self.assertEqual(queryset[1], self.cs)

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
        """Test the custom search field ordering is correct"""
        queryset = CustomSearchField.objects.all()
        field = create_custom_search_field(model=self.csm, name='body')

        self.assertEqual(queryset[0], field)
        self.assertEqual(queryset[1], self.csf)

    def test_custom_search_field_full_name(self):
        """Test full_field_method on custom search field"""
        field = create_custom_search_field(model=self.csm, name='title', selector='title_selector')

        self.assertEqual(field.full_field_name(), 'titletitle_selector')

        field = create_custom_search_field(model=self.csm, name='title')

        self.assertEqual(field.full_field_name(), 'title')

    def test_custom_search_sort_field_name(self):
        """Test sort_field_name on custom search field"""
        field = create_custom_search_field(
            model=self.csm,
            name='title',
            selector='title_selector',
            sort_selector='title_sort_selector'
        )

        self.assertEqual(field.sort_field_name(), 'titletitle_sort_selector')

        field = create_custom_search_field(
            model=self.csm,
            name='title',
            selector='title_selector'
        )

        self.assertEqual(field.sort_field_name(), 'titletitle_selector')

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
        """Test prepared_value method of custom search condition returns the correct value"""
        # This test is disabled because the date doesn't match, it needs to be mocked
        # condition = create_custom_search_condition(search=self.cs, field=self.csf, value='now()', match=14)
        # self.assertEqual(condition.prepared_value(), datetime.now())

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='2020', match=10)
        self.assertEqual(condition.prepared_value(), 2020)

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='false', match=18)
        self.assertEqual(condition.prepared_value(), False)

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='true', match=18)
        self.assertEqual(condition.prepared_value(), True)

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='contains', match=1)
        self.assertEqual(condition.prepared_value(), 'contains')

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='other', match=18)
        with self.assertRaises(ValidationError) as context:
            condition.prepared_value()
        self.assertTrue('Value is not a truth value.' in context.exception)

        condition = create_custom_search_condition(search=self.cs, field=self.csf, value='not int', match=10)
        with self.assertRaises(ValidationError) as context:
            condition.prepared_value()
        self.assertTrue('Value is not an integer.' in context.exception)

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
        """Test the custom search layout field ordering is correct"""
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

    def test_custom_search_ordering_order_by_field(self):
        """Test order_by_field method on custom search ordering"""
        field = create_custom_search_field(model=self.csm, name='title_field', sort_selector='title_selector')
        ordering = create_custom_search_ordering(search=self.cs, field=field, descending=False)

        order_by = ordering.order_by_field()
        self.assertEqual(order_by, 'title_fieldtitle_selector__min')

        field = create_custom_search_field(model=self.csm, name='body_field', sort_selector='body_selector')
        ordering = create_custom_search_ordering(search=self.cs, field=field, descending=True)

        order_by = ordering.order_by_field()
        self.assertEqual(order_by, '-body_fieldbody_selector__max')

        field = create_custom_search_field(model=self.csm, name='body_field')
        ordering = create_custom_search_ordering(search=self.cs, field=field, descending=True)

        order_by = ordering.order_by_field()
        self.assertEqual(order_by, '-body_field')

        field = create_custom_search_field(model=self.csm, name='body_field')
        ordering = create_custom_search_ordering(search=self.cs, field=field, descending=False)

        order_by = ordering.order_by_field()
        self.assertEqual(order_by, 'body_field')
