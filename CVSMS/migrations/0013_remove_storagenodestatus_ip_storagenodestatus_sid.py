# Generated by Django 4.1.7 on 2023-03-23 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CVSMS', '0012_alter_storagenodeinfo_sid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storagenodestatus',
            name='IP',
        ),
        migrations.AddField(
            model_name='storagenodestatus',
            name='SID',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
