# Generated by Django 4.1.1 on 2023-06-02 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CVSMS', '0022_alter_files_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='storagenodeinfo',
            name='SFTPport',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
