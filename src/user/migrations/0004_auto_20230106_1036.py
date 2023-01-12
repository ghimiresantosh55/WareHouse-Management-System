# Generated by Django 3.2 on 2023-01-06 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0003_department_allow_sales'),
        ('user', '0003_user_department'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='department',
        ),
        migrations.AddField(
            model_name='user',
            name='department',
            field=models.ManyToManyField(to='department.Department'),
        ),
    ]
