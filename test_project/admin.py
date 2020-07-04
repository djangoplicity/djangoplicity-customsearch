# -*- coding: utf-8 -*-
from django.contrib import admin
from djangoplicity.contrib.admin.sites import AdminSite
from djangoplicity.contrib.admin.discover import autoregister
from django.contrib import admin
from .models import Author, Article, Book, Entry

# Import all admin interfaces we need
import django.contrib.sites.admin
import djangoplicity.customsearch.admin

# Register each applications admin interfaces with
# an admin site.
admin_site = AdminSite(name="admin_site")
adminlogs_site = AdminSite(name="adminlogs_site")

autoregister(admin_site, django.contrib.auth.admin)
autoregister(admin_site, django.contrib.sites.admin)

autoregister(admin_site, djangoplicity.customsearch.admin)

admin.site.register(Article)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Entry)

adminlogs_site.register(django.contrib.sites.models.Site, django.contrib.sites.admin.SiteAdmin)

admin_site.register(django.contrib.auth.models.User, django.contrib.auth.admin.UserAdmin)

admin_site.register(django.contrib.auth.models.Group, django.contrib.auth.admin.GroupAdmin)
