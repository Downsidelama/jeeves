# Generated by Django 2.2.4 on 2019-11-01 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0019_pipelineresult_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipelineresult',
            name='branch',
            field=models.TextField(default='master'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pipelineresult',
            name='installation_id',
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pipelineresult',
            name='pull_request_number',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='pipelineresult',
            name='revision',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
