# Generated by Django 3.2 on 2023-01-12 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ppb', '0005_alter_ppbmain_ppb_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='ppbdetail',
            name='active',
            field=models.BooleanField(default=True, help_text='PPB Detail active status is default to True'),
        ),
    ]
