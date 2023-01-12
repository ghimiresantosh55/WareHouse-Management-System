# Generated by Django 3.2 on 2023-01-02 07:29

from django.db import migrations, models
import src.custom_lib.functions.field_value_validation


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('qty', models.DecimalField(decimal_places=2, max_digits=12, validators=[src.custom_lib.functions.field_value_validation.gt_zero_validator])),
                ('purchase_cost', models.DecimalField(decimal_places=2, default=0.0, help_text='purchase cost of order default=0.00', max_digits=12)),
                ('sale_cost', models.DecimalField(decimal_places=2, default=0.0, help_text='sale cost of order default=0.00', max_digits=12)),
                ('discountable', models.BooleanField(default=True, help_text='Check if item is discountable default=True')),
                ('taxable', models.BooleanField(default=True, help_text='Check if item is discountable default=True')),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Tax rate if item is taxable, default=0.00 max upto 100.00', max_digits=5)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='default = 0.00 ', max_digits=12)),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Discount rate if item is discountable, default=0.00 and max upto 100.00', max_digits=5)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='default = 0.00 ', max_digits=12)),
                ('gross_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='default = 0.00 ', max_digits=12)),
                ('net_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='default = 0.00 ', max_digits=12)),
                ('cancelled', models.BooleanField(default=False, help_text='Cancelled default = False')),
                ('picked', models.BooleanField(default=False, help_text='order picked from warehouse')),
                ('remarks', models.CharField(blank=True, max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('order_no', models.CharField(help_text='Order Id should be max. of 13 characters', max_length=20, unique=True)),
                ('status', models.PositiveIntegerField(choices=[(1, 'PENDING'), (2, 'BILLED'), (3, 'CANCELLED'), (4, 'CHALAN')], help_text='Where 1 = PENDING, 2 = BILLED,  3 = CANCELLED, 4 = CHALAN Default=1')),
                ('total_discount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total discount default=0.00', max_digits=12)),
                ('total_tax', models.DecimalField(decimal_places=2, default=0.0, help_text='Total tax default=0.00', max_digits=12)),
                ('sub_total', models.DecimalField(decimal_places=2, default=0.0, help_text='Sub total default=0.00', max_digits=12)),
                ('total_discountable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total discountable amount', max_digits=12)),
                ('total_taxable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total taxable amount', max_digits=12)),
                ('total_non_taxable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total nontaxable amount', max_digits=12)),
                ('delivery_date_ad', models.DateField(blank=True, help_text='Bill Date AD', max_length=10, null=True)),
                ('delivery_date_bs', models.CharField(blank=True, help_text='Bill Date BS', max_length=10)),
                ('delivery_location', models.CharField(blank=True, help_text='Location should be max. of 100 characters', max_length=100)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0.0, help_text='Grand total default=0.00', max_digits=12)),
                ('pick_verified', models.BooleanField(default=False, help_text='Customer order id picked from ware house')),
                ('remarks', models.CharField(blank=True, help_text='Remarks should be max. of 100 characters', max_length=100)),
                ('by_batch', models.BooleanField(default=False, help_text='True if customer order is placed batch wise, False if customer order is placed according to FIFO')),
                ('approved', models.BooleanField(default=False)),
                ('credit_term', models.PositiveIntegerField(blank=True, choices=[(15, '15 days'), (30, '30 days'), (45, '45 days'), (60, '60 days')], default=30, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
