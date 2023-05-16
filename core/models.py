from django.db import models
from django.contrib.auth.models import User
import pandas as pd


# Create your models here.


class PersonalPrediction(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    CSVFile = models.FileField(upload_to="CSVFiles")
    predictedData = models.TextField(null=True, blank=True)
    createdDateTime = models.DateTimeField(auto_now_add=True, null=True)

    def set_predictedData(self, df):
        self.predictedData = df.to_json()

    def get_predictedData(self):
        return pd.read_json(self.predictedData)


class UserHistory(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    predictionId = models.ForeignKey(PersonalPrediction, on_delete=models.CASCADE)


class CoinCategory(models.Model):
    category = models.CharField(max_length=30)

    def __str__(self):
        return self.category


class LSTMModel(models.Model):
    name = models.CharField(max_length=20)
    rmse = models.CharField(max_length=20)
    mape = models.CharField(max_length=20)
    machineLearningModel = models.FileField(upload_to="LstmModel", null=True)
    predictedData = models.TextField(null=True, blank=True)
    updateDateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProphetModel(models.Model):
    name = models.CharField(max_length=20)
    rmse = models.CharField(max_length=20)
    mape = models.CharField(max_length=20)
    machineLearningModel = models.FileField(upload_to="ProphetModel", null=True)
    predictedData = models.TextField(null=True, blank=True)
    createDateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class NHitsModel(models.Model):
    name = models.CharField(max_length=20)
    rmse = models.CharField(max_length=20)
    mape = models.CharField(max_length=20)
    machineLearningModel = models.FileField(upload_to="NHitsModel", null=True)
    predictedData = models.TextField(null=True, blank=True)
    createDateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cryptocurrencies(models.Model):
    coinName = models.CharField(max_length=30)
    symbol = models.CharField(max_length=10)
    logoImage = models.FileField(
        upload_to="cryptocurrenciesLogo", null=True, blank=True
    )
    categoryId = models.ForeignKey(CoinCategory, on_delete=models.CASCADE)
    lastPrice = models.CharField(max_length=30, null=True)
    historicalData = models.TextField(null=True, blank=True)
    lstmId = models.ForeignKey(
        LSTMModel, on_delete=models.CASCADE, blank=True, null=True
    )
    prophetId = models.ForeignKey(
        ProphetModel, on_delete=models.CASCADE, blank=True, null=True
    )
    NhitsId = models.ForeignKey(
        NHitsModel, on_delete=models.CASCADE, blank=True, null=True
    )
    updateDateTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.coinName

    def set_historicalData(self, df):
        self.historicalData = df.to_json()

    def set_predictedData(self, df):
        self.predictedData = df.to_json()

    def get_historicalData(self):
        return pd.read_json(self.historicalData)

    def get_predictedData(self):
        return pd.read_json(self.predictedData)
