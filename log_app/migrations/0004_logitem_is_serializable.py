# Generated by Django 3.2 on 2023-01-02 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log_app', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='logitem',
            name='is_serializable',
            field=models.BooleanField(default=True),
        ),
    ]