# Generated by Django 2.2.4 on 2019-10-20 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_pipelineresult_build_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipelineresult',
            name='build_end_time',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]