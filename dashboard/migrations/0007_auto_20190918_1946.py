# Generated by Django 2.2.4 on 2019-09-18 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_auto_20190918_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipelineresults',
            name='status',
            field=models.IntegerField(default=1),
        ),
    ]