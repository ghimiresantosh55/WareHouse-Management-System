# Generated by Django 3.2 on 2023-01-02 07:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('purchase', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer_order', '0001_initial'),
        ('core_app', '0002_initial'),
        ('customer', '0003_initial'),
        ('item', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermaster',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='customer_order_approved', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordermaster',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordermaster',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='customer.customer'),
        ),
        migrations.AddField(
            model_name='ordermaster',
            name='discount_scheme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core_app.discountscheme'),
        ),
        migrations.AddField(
            model_name='ordermaster',
            name='verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='customer_order_verified', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.item'),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='item_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='item.itemcategory'),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_details', to='customer_order.ordermaster'),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='picked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='order_details_picked', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='purchase_detail',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='purchase.purchasedetail'),
        ),
    ]
