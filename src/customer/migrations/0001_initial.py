# Generated by Django 3.2 on 2023-01-02 07:29

from django.db import migrations, models
import django.db.models.deletion
import src.custom_lib.functions.field_value_validation
import src.customer.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('first_name', models.CharField(help_text='First name should be max. of 40 characters', max_length=40)),
                ('middle_name', models.CharField(blank=True, help_text='Middle name should be max. of 40 characters', max_length=40)),
                ('last_name', models.CharField(blank=True, help_text='Last name should be max. of 40 characters', max_length=40)),
                ('address', models.CharField(help_text='Address should be max. of 50 characters', max_length=50)),
                ('phone_no', models.CharField(blank=True, help_text='Phone no. should be max. of 15 characters', max_length=15)),
                ('mobile_no', models.CharField(blank=True, help_text='mobile no. should be max. of 15 characters', max_length=15)),
                ('email_id', models.CharField(blank=True, help_text='Email Id should be max. of 50 characters', max_length=50)),
                ('pan_vat_no', models.CharField(blank=True, help_text='PAN/VAT should be max. of 15 characters', max_length=9)),
                ('tax_reg_system', models.PositiveIntegerField(choices=[(1, 'VAT'), (2, 'PAN')], default=1, help_text='default value is 1')),
                ('image', models.ImageField(blank=True, help_text='max image size should be 2 MB', upload_to='customer', validators=[src.customer.models.validate_image])),
                ('active', models.BooleanField(default=True)),
                ('credit_limit', models.DecimalField(decimal_places=2, default=100000.0, max_digits=12, validators=[src.custom_lib.functions.field_value_validation.gt_zero_validator])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomerIsSupplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_is_supplier', to='customer.customer')),
            ],
        ),
    ]