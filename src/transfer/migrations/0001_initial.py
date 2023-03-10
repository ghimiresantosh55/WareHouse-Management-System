# Generated by Django 3.2 on 2023-01-02 07:29

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TransferDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('cost', models.DecimalField(decimal_places=2, default=0.0, help_text='cost can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('qty', models.DecimalField(decimal_places=2, help_text='Purchase quantity can have max value upto=9999999999.99 and min_value=0.0', max_digits=12)),
                ('pack_qty', models.DecimalField(decimal_places=2, help_text="pack quantity can't be negative", max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('taxable', models.BooleanField(default=True, help_text='Check if item is taxable')),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Tax rate if item is taxable, max_value=100.00 and default=0.0', max_digits=5)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Tax amount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('discountable', models.BooleanField(default=True, help_text='Check if item is discountable')),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Discount rate if item is discountable, max_value=100.00 and default=0.0', max_digits=5)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Discount amount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('gross_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Gross amount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('net_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Net amount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('cancelled', models.BooleanField(default=False)),
                ('is_picked', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransferMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('transfer_type', models.CharField(choices=[(1, 'TRANSFER'), (2, 'RETURN')], max_length=20)),
                ('transfer_no', models.CharField(help_text='Transfer No should be of max 20 characters', max_length=20, unique=True)),
                ('sub_total', models.DecimalField(decimal_places=2, default=0.0, help_text='Sub total can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Discount rate if applicable, default=0.0 and max_value upto=100.00', max_digits=5)),
                ('total_discountable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total discountable amount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('total_taxable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total taxable amount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('total_non_taxable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total nontaxable amount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('total_discount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total discount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('total_tax', models.DecimalField(decimal_places=2, default=0.0, help_text='Total tax can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0.0, help_text='Grand total can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('branch', models.PositiveIntegerField()),
                ('branch_name', models.CharField(blank=True, max_length=100)),
                ('remarks', models.CharField(blank=True, help_text='Remarks should be max. of 100 characters and blank=True', max_length=100)),
                ('return_dropped', models.BooleanField(default=True, help_text='True if items are dropped to locations after returning')),
                ('active', models.BooleanField(default=True, help_text='By default active=True')),
                ('is_transferred', models.BooleanField(default=False)),
                ('cancelled', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransferOrderDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('cost', models.DecimalField(decimal_places=2, default=0.0, help_text='cost can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('qty', models.DecimalField(decimal_places=2, help_text='Purchase quantity can have max value upto=9999999999.99 and min_value=0.0', max_digits=12)),
                ('pack_qty', models.DecimalField(decimal_places=2, help_text="pack quantity can't be negative", max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('cancelled', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransferOrderMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('transfer_order_no', models.CharField(help_text='Transfer No should be of max 20 characters', max_length=20, unique=True)),
                ('branch', models.PositiveIntegerField()),
                ('remarks', models.CharField(blank=True, help_text='Remarks should be max. of 100 characters and blank=True', max_length=100)),
                ('cancelled', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
