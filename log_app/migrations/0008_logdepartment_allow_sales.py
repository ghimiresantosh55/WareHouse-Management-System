# Generated by Django 3.2 on 2023-01-04 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log_app', '0007_loguser_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='logdepartment',
            name='allow_sales',
            field=models.BooleanField(default=False),
        ),
    ]