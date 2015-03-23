# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomSearch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'custom searches',
                'permissions': [('can_view', 'Can view all custom searches')],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomSearchCondition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exclude', models.BooleanField(default=False)),
                ('match', models.CharField(max_length=30, choices=[(b'__exact', b'Exact'), (b'__contains', b'Contains'), (b'__startswith', b'Starts with'), (b'__endswith', b'Ends with'), (b'__regex', b'Regular expression'), (b'__iexact', b'Exact (case-insensitive)'), (b'__icontains', b'Contains (case-insensitive)'), (b'__istartswith', b'Starts with (case-insensitive)'), (b'__iendswith', b'Ends with (case-insensitive)'), (b'__iregex', b'Regular expression (case-insensitive)'), (b'__year', b'Year'), (b'__month', b'Month'), (b'__day', b'Day'), (b'__week_day', b'Week day'), (b'__gt', b'Greater than'), (b'__gte', b'Greater than or equal to'), (b'__lt', b'Less than'), (b'__lte', b'Less than or equal to'), (b'__isnull', b'Is null'), (b'__gt', b'After'), (b'__lte', b'Before')])),
                ('value', models.CharField(max_length=255, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomSearchField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('field_name', models.SlugField()),
                ('selector', models.SlugField(blank=True)),
                ('sort_selector', models.SlugField(blank=True)),
                ('enable_layout', models.BooleanField(default=True)),
                ('enable_search', models.BooleanField(default=True)),
                ('enable_freetext', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['model__name', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomSearchGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomSearchLayout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomSearchLayoutField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveIntegerField(null=True, blank=True)),
                ('expand_rel', models.BooleanField(default=False)),
                ('field', models.ForeignKey(to='customsearch.CustomSearchField')),
                ('layout', models.ForeignKey(to='customsearch.CustomSearchLayout')),
            ],
            options={
                'ordering': ['position', 'id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomSearchModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('model', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomSearchOrdering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descending', models.BooleanField(default=False)),
                ('field', models.ForeignKey(to='customsearch.CustomSearchField')),
                ('search', models.ForeignKey(to='customsearch.CustomSearch')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='customsearchlayout',
            name='fields',
            field=models.ManyToManyField(to='customsearch.CustomSearchField', through='customsearch.CustomSearchLayoutField'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customsearchlayout',
            name='model',
            field=models.ForeignKey(to='customsearch.CustomSearchModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customsearchfield',
            name='model',
            field=models.ForeignKey(to='customsearch.CustomSearchModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customsearchcondition',
            name='field',
            field=models.ForeignKey(to='customsearch.CustomSearchField'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customsearchcondition',
            name='search',
            field=models.ForeignKey(to='customsearch.CustomSearch'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customsearch',
            name='group',
            field=models.ForeignKey(blank=True, to='customsearch.CustomSearchGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customsearch',
            name='layout',
            field=models.ForeignKey(to='customsearch.CustomSearchLayout'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customsearch',
            name='model',
            field=models.ForeignKey(to='customsearch.CustomSearchModel'),
            preserve_default=True,
        ),
    ]
