# Generated by Django 2.2.3 on 2019-08-20 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20190820_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipeline',
            name='repo_url',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='pipeline',
            name='script',
            field=models.TextField(blank=True, default=''),
        ),
    ]
