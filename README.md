# Djangoplicity Customsearch

![Coverage](https://img.shields.io/codecov/c/github/djangoplicity/djangoplicity-customsearch/develop)
![Size](https://img.shields.io/github/repo-size/djangoplicity/djangoplicity-customsearch)
![License](https://img.shields.io/github/license/djangoplicity/djangoplicity-customsearch)
![Language](https://img.shields.io/github/languages/top/djangoplicity/djangoplicity-customsearch)

Djangoplicity Customsearch is a dependency of the [Djangoplicity](https://github.com/djangoplicity/djangoplicity) CMS
created by the European Southern Observatory (ESO) for managing internal searches.

## Installation
Djangoplicity Customsearch actually supports Python 2.7 and Python 3+.

You must install Djangoplicity Customsearch using the Github repository, so add the following packages to your
requirements depending on the Python version you are using.
```
# For Python 3+
git+https://@github.com/djangoplicity/djangoplicity.git@release/python3

git+https://@github.com/djangoplicity/djangoplicity-customsearch.git@release/python3

# For Python 2.7
git+https://@github.com/djangoplicity/djangoplicity.git@develop

git+https://@github.com/djangoplicity/djangoplicity-customsearch.git@develop

# Asynchronous Task Queue
celery==4.4.7
```
Celery is also required for some asynchronous tasks to work.

Now include the package in your `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...,
    'djangoplicity.admincomments',
    'djangoplicity.customsearch',
]
```

Djangoplicity requires some additional settings in order to work, so add this configuration to your `settings.py` 
file (you don't have to include those files in your assets):
```python
# JAVASCRIPT CUSTOM CONFIG
JQUERY_JS = "jquery/jquery-1.11.1.min.js"
JQUERY_UI_JS = "jquery-ui-1.12.1/jquery-ui.min.js"
JQUERY_UI_CSS = "jquery-ui-1.12.1/jquery-ui.min.css"
DJANGOPLICITY_ADMIN_CSS = "djangoplicity/css/admin.css"
DJANGOPLICITY_ADMIN_JS = "djangoplicity/js/admin.js"
SUBJECT_CATEGORY_CSS = "djangoplicity/css/widgets.css"
```

Next, you have to register the models in your `admin.py` file.
```python
# Import all admin interfaces we need
import django.contrib.sites.admin
from djangoplicity.contrib.admin.discover import autoregister
from djangoplicity.contrib.admin.sites import AdminSite
import djangoplicity.customsearch.admin

# Register each applications admin interfaces with
# an admin site.
admin_site = AdminSite(name="admin_site")

autoregister(admin_site, django.contrib.auth.admin)
autoregister(admin_site, django.contrib.sites.admin)

autoregister(admin_site, djangoplicity.customsearch.admin)
admin_site.register(django.contrib.auth.models.User, django.contrib.auth.admin.UserAdmin)
admin_site.register(django.contrib.auth.models.Group, django.contrib.auth.admin.GroupAdmin)

```
