# Generated by Django 2.2.4 on 2019-10-13 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_auto_20191013_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipeline',
            name='repository_id',
            field=models.IntegerField(default=None, null=True, unique=True),
        ),
    ]
