# Generated by Django 3.2 on 2023-01-02 07:29

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import src.item.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GenericName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('name', models.CharField(help_text='Generic name should be max. of 150 characters', max_length=150, unique=True)),
                ('active', models.BooleanField(default=True, help_text='By default active=True')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('name', models.CharField(help_text='Item name should be max. of 100 characters', max_length=100, unique=True)),
                ('code', models.CharField(blank=True, help_text='Item code should be max. of 40 characters', max_length=40, unique=True)),
                ('harmonic_code', models.CharField(blank=True, help_text='harmonic code max length 50', max_length=50)),
                ('item_type', models.PositiveIntegerField(choices=[(1, 'INVENTORY'), (2, 'SALE'), (3, 'BOTH')], default=3, help_text='Item type like 1=INVENTORY, 2=SALE, 3=BOTH and default = BOTH')),
                ('stock_alert_qty', models.IntegerField(default=1, help_text='Quantity for alert/warning')),
                ('location', models.CharField(blank=True, help_text='Physical location of item, max length can be of 10 characters and blank= True, null= True', max_length=10, null=True)),
                ('basic_info', models.TextField(blank=True, help_text='Basic info can text field', null=True)),
                ('taxable', models.BooleanField(default=True, help_text='Check if item is taxable, default=True')),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Tax rate if item is taxable, default=0.0 and can be upto 100.00', max_digits=5)),
                ('discountable', models.BooleanField(default=True, help_text='Check if item is discountable, default=True')),
                ('expirable', models.BooleanField(default=True, help_text='Check if item is expirable, default=True')),
                ('purchase_cost', models.DecimalField(decimal_places=2, default=0.0, help_text='Max value purchase_cost can be upto 9999999999.99', max_digits=12)),
                ('sale_cost', models.DecimalField(decimal_places=2, default=0.0, help_text='Max value sale_cost can be upto 9999999999.99', max_digits=12)),
                ('image', models.ImageField(blank=True, default='default_images/product.png', upload_to='item', validators=[src.item.models.validate_image])),
                ('depreciation_method', models.PositiveIntegerField(choices=[(1, 'STRAIGHT-LINE'), (2, 'DIMINISHING BALANCE'), (3, 'UNIT OF PRODUCT METHOD')], default=1, help_text='Item type like 1=STRAIGHT-LINE, 2=DIMINISHING BALANCE, 3=UNIT OF PRODUCT METHOD')),
                ('depreciation_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Max. value: 100', max_digits=7)),
                ('depreciation_year', models.DecimalField(decimal_places=2, default=0.0, help_text='-', max_digits=7)),
                ('salvage_value', models.DecimalField(decimal_places=2, default=0.0, help_text='Salvage value', max_digits=12)),
                ('model_no', models.CharField(blank=True, help_text='Model no. of item', max_length=30, null=True)),
                ('fixed_asset', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True, help_text='By default active=True')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('name', models.CharField(help_text='Category name can be max. of 100 characters', max_length=100, unique=True)),
                ('code', models.CharField(blank=True, help_text='Item code can be max. of 10 characters', max_length=10, unique=True)),
                ('display_order', models.IntegerField(blank=True, default=0, help_text='Display order for ordering, default=0 and blank= True, null= True', null=True)),
                ('active', models.BooleanField(default=True, help_text='By default active=True')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('name', models.CharField(help_text='Manufacturer name should be max. of 100 characters', max_length=100, unique=True)),
                ('active', models.BooleanField(default=True, help_text='By default active=True')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PackingType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('name', models.CharField(help_text=' name can be max. of 50 characters', max_length=50, unique=True)),
                ('short_name', models.CharField(help_text=' short name can be max. of 5 characters', max_length=5, unique=True)),
                ('active', models.BooleanField(default=True, help_text='By default active=True')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PackingTypeDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('pack_qty', models.DecimalField(decimal_places=2, help_text="Value can't be negative", max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('active', models.BooleanField(default=True, help_text='By default active=True')),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('name', models.CharField(help_text='Unit name can be max. of 50 characters and must be unique', max_length=50, unique=True)),
                ('short_form', models.CharField(help_text='short_form can be max. of 20 characters and must be unique', max_length=20, unique=True)),
                ('display_order', models.IntegerField(blank=True, default=0, help_text='Display order for ordering, default=0,blank= True, null= True', null=True)),
                ('active', models.BooleanField(default=True, help_text='By default active=True')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]