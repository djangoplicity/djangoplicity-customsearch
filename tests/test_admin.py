from datetime import datetime
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from test_project.models import Entry
from .utils import (
    create_custom_search, create_custom_search_model,
    create_custom_search_field, create_custom_search_group,
    create_custom_search_layout_field, create_custom_search_layout, create_custom_search_condition
)


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@customsearch.org',
            password='password123'
        )
        self.client.force_login(self.admin_user)

    @classmethod
    def setUpTestData(cls):
        cls.csm = create_custom_search_model(name='Entry Custom Search Model', model=Entry)
        cls.csf = create_custom_search_field(model=cls.csm, name='title')
        cls.csg = create_custom_search_group(name='Custom Search Group')
        cls.csl = create_custom_search_layout(model=cls.csm, name=cls.csm.name)
        cls.cslf = create_custom_search_layout_field(layout=cls.csl, field=cls.csf)
        cls.cs = create_custom_search(model=cls.csm, group=cls.csg, layout=cls.csl)

    def test_custom_search_pages(self):
        """Test that custom search models are listed"""
        models = ['customsearchmodel', 'customsearchcondition', 'customsearchlayout', 'customsearch']
        for model in models:
            url = reverse('admin:customsearch_%s_changelist' % model)
            res = self.client.get(url)

            self.assertEqual(res.status_code, 200)

    def test_custom_searches_listed(self):
        """Test that searches are listed on change list page"""
        url = reverse('admin:customsearch_customsearch_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.cs.name)
        self.assertContains(res, self.csm.name)
        self.assertContains(res, self.csg.name)
        self.assertContains(res, 'Export')
        self.assertContains(res, 'Results')
        self.assertContains(res, 'Labels')

    def test_custom_search_search_page(self):
        """Test that searches are listed on search page"""
        create_custom_search_condition(search=self.cs, field=self.csf, value='Lorem', match=1)
        entry = Entry.objects.create(
            title='Lorem ipsum dolor sit amet, consectetur adipiscing',
            body='Quisque velit ipsum, suscipit non ultricies vitae, luctus eget urna. Suspendisse feugiat ac massa.',
            pub_date=datetime.now()
        )
        url = "/admin/customsearch/customsearch/%s/search/?s=Lorem&p=not_a_number" % self.cs.pk
        res = self.client.get(url)

        self.assertContains(res, 'Custom Search: %s' % self.cs.name)
        self.assertContains(res, entry.title)
        self.assertContains(res, 'Include entrys where title contains &quot;Lorem&quot;.')

    def test_custom_search_search_page_status_200_invalid_page(self):
        """Test that response returns status code 200 even if search and page params are not valid"""
        url = "/admin/customsearch/customsearch/%s/search/?s=not_a_valid_term&p=200" % self.cs.pk
        res = self.client.get(url)
        self.assertEquals(res.status_code, 200)
        self.assertContains(res, '<strong>Total:</strong> 0', html=True)

    def test_custom_search_labels_page(self):
        """Test that labels page returns an error message because djangoplicity-contacts is not installed"""
        url = reverse('admin:customsearch_customsearch_labels', args=[self.cs.pk])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Labels generation support not available.')

    def test_custom_search_change_page(self):
        """Test that custom search change page shows human readable text and action buttons"""
        create_custom_search_condition(search=self.cs, field=self.csf, value='Lorem', match=1)

        url = reverse('admin:customsearch_customsearch_change', args=[self.cs.pk])
        res = self.client.get(url)

        self.assertEquals(res.status_code, 200)
        self.assertContains(res, 'Change custom search')
        self.assertContains(res, 'Search results')
        self.assertContains(res, 'Labels')
        self.assertContains(res, 'Export')
        self.assertContains(res, 'Include entrys where title contains &quot;Lorem&quot;.')
