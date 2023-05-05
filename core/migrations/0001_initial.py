# Generated by Django 4.2 on 2023-05-05 13:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CoinCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Cryptocurrencies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coinName', models.CharField(max_length=30)),
                ('symbol', models.CharField(max_length=10)),
                ('logoImage', models.FileField(null=True, upload_to='cryptocurrenciesLogo')),
                ('lastPrice', models.CharField(max_length=30, null=True)),
                ('historicalData', models.TextField(blank=True, null=True)),
                ('predictedData', models.TextField(null=True)),
                ('updateDateTime', models.DateTimeField(auto_now_add=True)),
                ('categoryId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.coincategory')),
            ],
        ),
        migrations.CreateModel(
            name='LSTMModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('rmse', models.CharField(max_length=20)),
                ('mape', models.CharField(max_length=20)),
                ('machineLearningModel', models.FileField(null=True, upload_to='machineLearningModels')),
                ('updateDateTime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PersonalPrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CSVFile', models.FileField(upload_to='CSVFiles')),
                ('predictedData', models.TextField(null=True)),
                ('createdDateTime', models.DateTimeField(auto_now_add=True, null=True)),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProphetScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('rmse', models.CharField(max_length=20)),
                ('mape', models.CharField(max_length=20)),
                ('createDateTime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predictionId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.personalprediction')),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SystemPrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predictedData', models.TextField()),
                ('createdDateTime', models.DateTimeField(auto_now_add=True)),
                ('coinId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.cryptocurrencies')),
            ],
        ),
        migrations.AddField(
            model_name='cryptocurrencies',
            name='lstmModelId',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.lstmmodel'),
        ),
        migrations.AddField(
            model_name='cryptocurrencies',
            name='prophetId',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.prophetscore'),
        ),
    ]
