# Generated by Django 2.2.4 on 2019-11-23 18:20

from django.db import migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0023_pipelineresult_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipelineresult',
            name='command',
            field=picklefield.fields.PickledObjectField(editable=False, null=True),
        ),
    ]
