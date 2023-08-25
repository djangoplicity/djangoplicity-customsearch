# Generated by Django 3.1 on 2022-08-03 12:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customsearch', '0002_customsearchcondition_and_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customsearchcondition',
            name='and_together',
            field=models.BooleanField(default=False, help_text='"AND" conditions together instead of "OR"'),
        ),
        migrations.AlterField(
            model_name='customsearchcondition',
            name='field',
            field=models.ForeignKey(limit_choices_to={'enable_search': True}, on_delete=django.db.models.deletion.CASCADE, to='customsearch.customsearchfield'),
        ),
        migrations.AlterField(
            model_name='customsearchcondition',
            name='match',
            field=models.CharField(choices=[('__exact', 'Exact'), ('__contains', 'Contains'), ('__startswith', 'Starts with'), ('__endswith', 'Ends with'), ('__regex', 'Regular expression'), ('__iexact', 'Exact (case-insensitive)'), ('__icontains', 'Contains (case-insensitive)'), ('__istartswith', 'Starts with (case-insensitive)'), ('__iendswith', 'Ends with (case-insensitive)'), ('__iregex', 'Regular expression (case-insensitive)'), ('__year', 'Year'), ('__month', 'Month'), ('__day', 'Day'), ('__week_day', 'Week day'), ('__gt', 'Greater than'), ('__gte', 'Greater than or equal to'), ('__lt', 'Less than'), ('__lte', 'Less than or equal to'), ('__isnull', 'Is null'), ('__gt', 'After'), ('__lte', 'Before')], max_length=30),
        ),
        migrations.AlterField(
            model_name='customsearchlayoutfield',
            name='field',
            field=models.ForeignKey(limit_choices_to={'enable_layout': True}, on_delete=django.db.models.deletion.CASCADE, to='customsearch.customsearchfield'),
        ),
        migrations.AlterField(
            model_name='customsearchordering',
            name='field',
            field=models.ForeignKey(limit_choices_to={'enable_search': True}, on_delete=django.db.models.deletion.CASCADE, to='customsearch.customsearchfield'),
        ),
    ]