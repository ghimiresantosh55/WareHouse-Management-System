# Generated by Django 3.2 on 2023-01-02 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Repair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('repair_status', models.PositiveIntegerField(choices=[(1, 'PENDING'), (2, 'COMPLETED'), (3, 'CANCELED')], default=1, help_text='where 1=PENDING, 2= COMPLETED, 3=CANCELED')),
                ('expected_date_to_repair_ad', models.DateField(blank=True, help_text='Expected Date To Repair AD, blank = True', null=True)),
                ('expected_date_to_repair_bs', models.CharField(blank=True, help_text='Expected Date To Repair BS, blank = True', max_length=10)),
                ('total_repair_cost', models.DecimalField(decimal_places=2, default=0.0, help_text='Total discountable amount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RepairDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('problem_description', models.CharField(blank=True, help_text='max length can be upto 200 and blank = true', max_length=200)),
                ('repair_cost', models.DecimalField(decimal_places=2, default=0.0, help_text='Total discountable amount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RepairUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('device_type', models.PositiveBigIntegerField(choices=[(1, 'Mobile'), (2, 'PC'), (3, 'Tablet'), (4, 'Other'), (5, 'NA')], default=5, help_text='where 1=Mobile, 2=PC, 3=Tablet and 4=Other')),
                ('app_type', models.PositiveBigIntegerField(choices=[(1, 'Web-App'), (2, 'IOS-App'), (3, 'Android-App'), (4, 'NA')], default=4, help_text='where 1=Web-App, 2=IOS-APP, 3=Android-APP')),
                ('repair_status', models.PositiveIntegerField(choices=[(1, 'PENDING'), (2, 'COMPLETED'), (3, 'CANCELED')], default=1, help_text='where 1=PENDING, 2= COMPLETED, 3=CANCELED')),
                ('comments', models.CharField(blank=True, help_text='max length can be upto 200 and blank = true', max_length=200)),
                ('actions_performed', models.CharField(blank=True, help_text='max length can be upto 200 and blank = true', max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
