# Generated by Django 3.2 on 2023-01-02 07:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('item', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core_app', '0002_initial'),
        ('customer', '0003_initial'),
        ('sale', '0001_initial'),
        ('purchase', '0002_initial'),
        ('chalan', '0002_initial'),
        ('customer_order', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleprintlog',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='saleprintlog',
            name='sale_master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sale_masters', to='sale.salemaster'),
        ),
        migrations.AddField(
            model_name='salepaymentdetail',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='salepaymentdetail',
            name='payment_mode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core_app.paymentmode'),
        ),
        migrations.AddField(
            model_name='salepaymentdetail',
            name='sale_master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payment_details', to='sale.salemaster'),
        ),
        migrations.AddField(
            model_name='salemaster',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='salemaster',
            name='customer',
            field=models.ForeignKey(blank=True, help_text='null =True', null=True, on_delete=django.db.models.deletion.PROTECT, to='customer.customer'),
        ),
        migrations.AddField(
            model_name='salemaster',
            name='discount_scheme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core_app.discountscheme'),
        ),
        migrations.AddField(
            model_name='salemaster',
            name='fiscal_session_ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core_app.fiscalsessionad'),
        ),
        migrations.AddField(
            model_name='salemaster',
            name='fiscal_session_bs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core_app.fiscalsessionbs'),
        ),
        migrations.AddField(
            model_name='salemaster',
            name='ref_chalan_master',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chalan.chalanmaster'),
        ),
        migrations.AddField(
            model_name='salemaster',
            name='ref_order_master',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer_order.ordermaster'),
        ),
        migrations.AddField(
            model_name='salemaster',
            name='ref_sale_master',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sale.salemaster'),
        ),
        migrations.AddField(
            model_name='saledetail',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='saledetail',
            name='item',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.PROTECT, to='item.item'),
        ),
        migrations.AddField(
            model_name='saledetail',
            name='item_category',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.PROTECT, to='item.itemcategory'),
        ),
        migrations.AddField(
            model_name='saledetail',
            name='ref_chalan_detail',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='chalan.chalandetail'),
        ),
        migrations.AddField(
            model_name='saledetail',
            name='ref_order_detail',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='customer_order.orderdetail'),
        ),
        migrations.AddField(
            model_name='saledetail',
            name='ref_purchase_detail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchase_details', to='purchase.purchasedetail'),
        ),
        migrations.AddField(
            model_name='saledetail',
            name='ref_sale_detail',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sale.saledetail'),
        ),
        migrations.AddField(
            model_name='saledetail',
            name='sale_master',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.PROTECT, related_name='sale_details', to='sale.salemaster'),
        ),
        migrations.AddField(
            model_name='saleadditionalcharge',
            name='charge_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core_app.additionalchargetype'),
        ),
        migrations.AddField(
            model_name='saleadditionalcharge',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='saleadditionalcharge',
            name='sale_master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sale_additional_charges', to='sale.salemaster'),
        ),
        migrations.AddField(
            model_name='irduploadlog',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='irduploadlog',
            name='sale_master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sale.salemaster'),
        ),
    ]
