# Generated by Django 2.2.4 on 2019-09-15 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_pipeline_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='PipeLineResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
