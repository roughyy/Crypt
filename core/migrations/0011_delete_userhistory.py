# Generated by Django 4.2 on 2023-05-23 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_rename_nhitsid_cryptocurrencies_nhitsid'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserHistory',
        ),
    ]
