# Generated by Django 3.2 on 2023-01-02 07:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('audit', '0001_initial'),
        ('item_serialization', '0003_salepackingtypecode_transfer_detail'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditdetail',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='auditdetail',
            name='packing_type_detail_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='item_serialization.packingtypedetailcode'),
        ),
        migrations.AddField(
            model_name='audit',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
