# Generated by Django 3.2 on 2023-01-06 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0003_department_allow_sales'),
        ('purchase', '0004_auto_20230105_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseordermaster',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='department_purchase_orders', to='department.department'),
        ),
    ]