# Generated by Django 3.2 on 2023-01-04 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0002_auto_20230104_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='allow_sales',
            field=models.BooleanField(default=False),
        ),
    ]
