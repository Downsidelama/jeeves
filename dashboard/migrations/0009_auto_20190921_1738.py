# Generated by Django 2.2.4 on 2019-09-21 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_auto_20190918_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipelineresult',
            name='subversion',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='pipelineresult',
            name='version',
            field=models.IntegerField(default=1),
        ),
    ]
