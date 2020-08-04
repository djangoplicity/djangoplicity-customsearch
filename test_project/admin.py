# -*- coding: utf-8 -*-
# Import all admin interfaces we need
import django.contrib.sites.admin
from djangoplicity.contrib.admin.discover import autoregister
from djangoplicity.contrib.admin.sites import AdminSite

import djangoplicity.customsearch.admin
from .models import Author, Article, Book, Entry

# Register each applications admin interfaces with
# an admin site.
admin_site = AdminSite(name="admin_site")

autoregister(admin_site, django.contrib.auth.admin)
autoregister(admin_site, django.contrib.sites.admin)

autoregister(admin_site, djangoplicity.customsearch.admin)

admin_site.register(Article)
admin_site.register(Author)
admin_site.register(Book)
admin_site.register(Entry)

admin_site.register(django.contrib.auth.models.User, django.contrib.auth.admin.UserAdmin)

admin_site.register(django.contrib.auth.models.Group, django.contrib.auth.admin.GroupAdmin)
