# Generated by Django 4.2 on 2023-05-13 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_cryptocurrencies_logoimage_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SystemPrediction',
        ),
    ]
