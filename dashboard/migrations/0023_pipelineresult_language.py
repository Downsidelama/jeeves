# Generated by Django 2.2.4 on 2019-11-06 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0022_remove_pipeline_commit_sha'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipelineresult',
            name='language',
            field=models.TextField(default='Python 3.7'),
            preserve_default=False,
        ),
    ]
