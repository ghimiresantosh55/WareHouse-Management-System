# Generated by Django 3.2 on 2023-01-02 07:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('item', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='packingtypedetail',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='packingtypedetail',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='packing_type_details', to='item.item'),
        ),
        migrations.AddField(
            model_name='packingtypedetail',
            name='packing_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='packing_types', to='item.packingtype'),
        ),
        migrations.AddField(
            model_name='packingtype',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='itemcategory',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='item',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='item',
            name='generic_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='item.genericname'),
        ),
        migrations.AddField(
            model_name='item',
            name='item_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.itemcategory'),
        ),
        migrations.AddField(
            model_name='item',
            name='manufacturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item.manufacturer'),
        ),
        migrations.AddField(
            model_name='item',
            name='unit',
            field=models.ForeignKey(blank=True, help_text=' blank=True, null= True', null=True, on_delete=django.db.models.deletion.PROTECT, to='item.unit'),
        ),
        migrations.AddField(
            model_name='genericname',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='packingtypedetail',
            unique_together={('item', 'packing_type', 'pack_qty')},
        ),
    ]
