# Generated by Django 3.2 on 2023-01-05 07:40

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('department', '0003_department_allow_sales'),
        ('purchase', '0003_auto_20230104_1041'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('item', '0003_item_is_serializable'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepartmentTransferMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('transfer_no', models.CharField(help_text='Purchase no. should be max. of 10 characters', max_length=20, unique=True)),
                ('transfer_type', models.PositiveIntegerField(choices=[(1, 'DEPARTMENT_TRANSFER'), (2, 'RETURN')], help_text='Purchase type like 1= transfer, 2 = Return')),
                ('sub_total', models.DecimalField(decimal_places=2, help_text='Sub total can be max upto 9999999999.99', max_digits=12)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0.0, help_text='Grand total can be max upto 9999999999.99', max_digits=12)),
                ('bill_no', models.CharField(blank=True, help_text='Bill no.', max_length=20)),
                ('remarks', models.CharField(blank=True, help_text='Remarks can be max. of 100 characters', max_length=100)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('from_department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='department_transfer_from', to='department.department')),
                ('ref_department_transfer_master', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='department_transfer.departmenttransfermaster')),
                ('ref_purchase_master', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='purchase.purchasemaster')),
                ('to_department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='department_transfer_to', to='department.department')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DepartmentTransferDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('purchase_cost', models.DecimalField(decimal_places=2, default=0.0, help_text='purchase_cost can be max value upto 9999999999.99 and default=0.0', max_digits=12)),
                ('sale_cost', models.DecimalField(decimal_places=2, help_text='sale_cost can be max value upto 9999999999.99 and default=0.0', max_digits=12)),
                ('qty', models.DecimalField(decimal_places=2, help_text='Purchase quantity can be max value upto 9999999999.99 and default=0.0', max_digits=12)),
                ('pack_qty', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('expirable', models.BooleanField(default=False, help_text='Check if item is Expirable, default=False')),
                ('gross_amount', models.DecimalField(decimal_places=2, help_text='Gross amount can be max upto 9999999999.99 and default=0.0', max_digits=12)),
                ('net_amount', models.DecimalField(decimal_places=2, help_text='Net amount can be max upto 9999999999.99 and default=0.0', max_digits=12)),
                ('batch_no', models.CharField(help_text='Batch no. max length 20', max_length=20)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('department_transfer_master', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='department_transfer_details', to='department_transfer.departmenttransfermaster')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.item')),
                ('item_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.itemcategory')),
                ('packing_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.packingtype')),
                ('packing_type_detail', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.packingtypedetail')),
                ('ref_department_transfer_detail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='department_transfer.departmenttransferdetail')),
                ('ref_purchase_detail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='department_transfer_detail', to='purchase.purchasedetail')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
