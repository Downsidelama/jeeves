# Generated by Django 2.2.4 on 2019-11-06 18:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_pipelineresult_log_file_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pipeline',
            name='commit_sha',
        ),
    ]