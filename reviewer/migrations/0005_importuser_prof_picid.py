# Generated by Django 3.0.4 on 2020-03-29 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviewer', '0004_auto_20200328_0350'),
    ]

    operations = [
        migrations.AddField(
            model_name='importuser',
            name='prof_picID',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Prof Pic ID'),
        ),
    ]
