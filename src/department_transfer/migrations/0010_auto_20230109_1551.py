# Generated by Django 3.2 on 2023-01-09 10:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('department_transfer', '0009_departmenttransfermaster_cancelled'),
    ]

    operations = [
        migrations.RenameField(
            model_name='departmenttransferdetail',
            old_name='cancelled',
            new_name='is_cancelled',
        ),
        migrations.RenameField(
            model_name='departmenttransfermaster',
            old_name='cancelled',
            new_name='is_cancelled',
        ),
    ]
