# Generated by Django 3.2 on 2023-01-08 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0005_purchaseordermaster_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasemaster',
            name='purchase_type',
            field=models.PositiveIntegerField(choices=[(1, 'PURCHASE'), (2, 'RETURN'), (3, 'OPENING-STOCK'), (4, 'STOCK-ADDITION'), (5, 'STOCK-SUBTRACTION'), (6, 'STOCK-DEPARTMENT')], help_text='Purchase type like 1= Purchase, 2 = Return, 3 = Opening stock, 4 = stock-addition, 5 = stock-subtraction'),
        ),
    ]
