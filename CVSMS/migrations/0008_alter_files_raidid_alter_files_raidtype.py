# Generated by Django 4.1.7 on 2023-03-20 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CVSMS', '0007_alter_files_raidtype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files',
            name='RAIDid',
            field=models.IntegerField(default=-1, null=True),
        ),
        migrations.AlterField(
            model_name='files',
            name='RAIDtype',
            field=models.CharField(choices=[('NONE', 'NONE'), ('PARITY', 'PARITY'), ('1', '1'), ('0', '0')], default='NONE', max_length=7, null=True),
        ),
    ]
