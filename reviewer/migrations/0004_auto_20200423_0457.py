# Generated by Django 3.0.5 on 2020-04-22 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviewer', '0003_auto_20200422_0339'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='extra',
            field=models.BooleanField(default=False, verbose_name='Extra?'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='lab_lesson',
            field=models.BooleanField(default=False, verbose_name='Lab Lesson?'),
        ),
    ]