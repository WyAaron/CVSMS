# Generated by Django 4.1.7 on 2023-03-23 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CVSMS', '0013_remove_storagenodestatus_ip_storagenodestatus_sid'),
    ]

    operations = [
        migrations.AddField(
            model_name='storagenodeinfo',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
