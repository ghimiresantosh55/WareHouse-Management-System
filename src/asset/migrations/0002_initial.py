# Generated by Django 3.2 on 2023-01-02 07:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('asset', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('item_serialization', '0003_salepackingtypecode_transfer_detail'),
        ('item', '0001_initial'),
        ('warehouse_location', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assettransfer',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetsubcategory',
            name='asset_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='asset.assetcategory'),
        ),
        migrations.AddField(
            model_name='assetsubcategory',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetservice',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='asset.assetlist'),
        ),
        migrations.AddField(
            model_name='assetservice',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetmaintenance',
            name='asset_dispatch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='asset_maintenance', to='asset.assetdispatch'),
        ),
        migrations.AddField(
            model_name='assetmaintenance',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetmaintenance',
            name='issued_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='asset_maintenance_issued', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetlist',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_details', to='asset.asset'),
        ),
        migrations.AddField(
            model_name='assetlist',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetlist',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='asset_location', to='warehouse_location.location'),
        ),
        migrations.AddField(
            model_name='assetlist',
            name='packing_type_detail_code',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='item_serialization.packingtypedetailcode'),
        ),
        migrations.AddField(
            model_name='assetissue',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='asset.assetlist'),
        ),
        migrations.AddField(
            model_name='assetissue',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetissue',
            name='issued_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='asset_issued_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetissue',
            name='return_received_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='asset_return_received_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetdispatchdetail',
            name='asset_detail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='asset_dispatch_asset', to='asset.assetlist'),
        ),
        migrations.AddField(
            model_name='assetdispatchdetail',
            name='asset_dispatch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='asset_dispatches', to='asset.assetdispatch'),
        ),
        migrations.AddField(
            model_name='assetdispatchdetail',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetdispatchdetail',
            name='picked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dispatch_details_picked', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetdispatchdetail',
            name='ref_dispatch_detail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ref_asset_dispatch_detail', to='asset.assetdispatchdetail'),
        ),
        migrations.AddField(
            model_name='assetdispatch',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetdispatch',
            name='dispatch_by',
            field=models.ForeignKey(help_text='dispatch by user', on_delete=django.db.models.deletion.PROTECT, related_name='asset_dispatch_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetdispatch',
            name='dispatch_to',
            field=models.ForeignKey(help_text='dispatch to user', on_delete=django.db.models.deletion.PROTECT, related_name='asset_dispatch_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetdispatch',
            name='ref_dispatch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ref_asset_dispatch', to='asset.assetdispatch'),
        ),
        migrations.AddField(
            model_name='assetdispatch',
            name='returned_by',
            field=models.ForeignKey(help_text='Returned by user', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='asset_dispatch_return_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assetcategory',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='asset',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='asset.assetcategory'),
        ),
        migrations.AddField(
            model_name='asset',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='asset',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.item'),
        ),
        migrations.AddField(
            model_name='asset',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='asset.assetsubcategory'),
        ),
    ]