# Generated by Django 3.2 on 2023-01-11 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0008_purchasedetail_ref_department_transfer_detail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchasemaster',
            name='department_transfer_master_transfer_no',
        ),
        migrations.AddField(
            model_name='purchasemaster',
            name='ref_department_transfer_master',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
