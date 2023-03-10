# Generated by Django 3.2 on 2023-01-02 07:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('repair', '0001_initial'),
        ('item', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sale', '0001_initial'),
        ('customer', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='repairuser',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='repairuser',
            name='repair_detail',
            field=models.ForeignKey(help_text='blank = true', on_delete=django.db.models.deletion.PROTECT, related_name='repair_status', to='repair.repairdetail'),
        ),
        migrations.AddField(
            model_name='repairdetail',
            name='assigned_to',
            field=models.ForeignKey(blank=True, help_text='null= True, blank = true', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='repair_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='repairdetail',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='repairdetail',
            name='item',
            field=models.ForeignKey(blank=True, help_text='null= True, blank= True', null=True, on_delete=django.db.models.deletion.PROTECT, to='item.item'),
        ),
        migrations.AddField(
            model_name='repairdetail',
            name='repair',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='repair_details', to='repair.repair'),
        ),
        migrations.AddField(
            model_name='repairdetail',
            name='sale',
            field=models.ForeignKey(blank=True, help_text='null= True, blank = true', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='repair_sale_details', to='sale.salemaster'),
        ),
        migrations.AddField(
            model_name='repairdetail',
            name='sale_detail',
            field=models.ForeignKey(blank=True, help_text='null= True, blank = true', null=True, on_delete=django.db.models.deletion.PROTECT, to='sale.saledetail'),
        ),
        migrations.AddField(
            model_name='repair',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='repair',
            name='customer',
            field=models.ForeignKey(blank=True, help_text='null= True, blank = true', null=True, on_delete=django.db.models.deletion.PROTECT, to='customer.customer'),
        ),
    ]
