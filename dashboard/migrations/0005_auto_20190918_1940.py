# Generated by Django 2.2.4 on 2019-09-18 17:40

import dashboard.pipeline_status
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_auto_20190918_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipelineresults',
            name='results',
            field=models.IntegerField(default=dashboard.pipeline_status.PipeLineStatus(1)),
        ),
    ]