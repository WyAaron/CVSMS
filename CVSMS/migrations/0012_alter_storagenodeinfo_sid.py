# Generated by Django 4.1.7 on 2023-03-23 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CVSMS', '0011_storagenodeinfo_maxsize_alter_files_sid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storagenodeinfo',
            name='SID',
            field=models.CharField(max_length=50),
        ),
    ]