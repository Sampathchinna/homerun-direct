# Generated by Django 5.1.6 on 2025-05-05 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0004_alter_workreport_work_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workreport',
            name='notes',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
