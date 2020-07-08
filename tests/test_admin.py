from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from .test_general import (
    create_custom_search, create_custom_search_model,
    create_custom_search_field, create_custom_search_group,
    create_custom_search_layout_field, create_custom_search_layout
)
from test_project.models import Entry


class TestAdmin(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@djangoplicity.com',
            password='password123',
            username='admin'
        )
        self.client.force_login(self.admin_user)
        self.site = AdminSite()

    @classmethod
    def setUpTestData(cls):
        cls.csm = create_custom_search_model(name='Entry Custom Search Model', model=Entry)

        cls.csf = create_custom_search_field(model=cls.csm, name='title')

        cls.csg = create_custom_search_group(name='Custom Search Group')

        cls.csl = create_custom_search_layout(model=cls.csm, name=cls.csm.name)

        cls.cslf = create_custom_search_layout_field(layout=cls.csl, field=cls.csf)

        cls.cs = create_custom_search(model=cls.csm, group=cls.csg, layout=cls.csl)

    def test_customsearches_listed(self):
        url = reverse('admin:customsearch_customsearch_changelist')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.cs.name)

    def test_customsearch_conditions_listed(self):
        url = reverse('admin:customsearch_customsearchcondition_changelist')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_customsearch_models_listed(self):
        url = reverse('admin:customsearch_customsearchmodel_changelist')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_customsearch_layouts_listed(self):
        url = reverse('admin:customsearch_customsearchlayout_changelist')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_customsearch_groups_listed(self):
        url = reverse('admin:customsearch_customsearchgroup_changelist')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
