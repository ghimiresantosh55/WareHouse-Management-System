# Generated by Django 3.2 on 2023-01-05 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('department_transfer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departmenttransfermaster',
            name='transfer_type',
            field=models.PositiveIntegerField(choices=[(1, 'TRANSFER'), (2, 'RETURN')], help_text='Purchase type like 1= transfer, 2 = Return'),
        ),
    ]
