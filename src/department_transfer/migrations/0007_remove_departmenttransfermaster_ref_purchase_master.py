# Generated by Django 3.2 on 2023-01-09 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('department_transfer', '0006_remove_departmenttransferdetail_batch_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='departmenttransfermaster',
            name='ref_purchase_master',
        ),
    ]
