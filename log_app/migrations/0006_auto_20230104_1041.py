# Generated by Django 3.2 on 2023-01-04 04:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0002_auto_20230104_1041'),
        ('log_app', '0005_logdepartment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='logdepartment',
            name='app_type',
        ),
        migrations.RemoveField(
            model_name='logdepartment',
            name='device_type',
        ),
        migrations.AddField(
            model_name='loglocation',
            name='department',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='department.department'),
        ),
        migrations.AddField(
            model_name='logpurchasemaster',
            name='department',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='department.department'),
        ),
        migrations.AlterField(
            model_name='logpurchasemaster',
            name='purchase_type',
            field=models.PositiveIntegerField(choices=[(1, 'PURCHASE'), (2, 'RETURN'), (3, 'OPENING-STOCK'), (4, 'STOCK-ADDITION'), (5, 'STOCK-SUBTRACTION'), (5, 'STOCK-DEPARTMENT')], help_text='Purchase type like 1= Purchase, 2 = Return, 3 = Opening stock, 4 = stock-addition, 5 = stock-subtraction'),
        ),
    ]