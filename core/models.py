from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class PersonalPrediction(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    CSVFile = models.FileField(upload_to="CSVFiles")
    predictedData = models.TextField(null=True)
    createdDateTime = models.DateTimeField(auto_now_add=True, null=True)


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
    machineLearningModel = models.FileField(
        upload_to="machineLearningModels", null=True
    )
    updateDateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProphetScore(models.Model):
    name = models.CharField(max_length=20)
    rmse = models.CharField(max_length=20)
    mape = models.CharField(max_length=20)
    createDateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cryptocurrencies(models.Model):
    coinName = models.CharField(max_length=30)
    symbol = models.CharField(max_length=10)
    logoImage = models.FileField(upload_to="cryptocurrenciesLogo", null=True)
    categoryId = models.ForeignKey(CoinCategory, on_delete=models.CASCADE)
    lastPrice = models.CharField(max_length=30, null=True)
    historicalData = models.TextField(null=True, blank=True)
    predictedData = models.TextField(null=True)
    lstmModelId = models.ForeignKey(
        LSTMModel, on_delete=models.CASCADE, blank=True, null=True
    )
    prophetId = models.ForeignKey(
        ProphetScore, on_delete=models.CASCADE, blank=True, null=True
    )
    updateDateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.coinName


class SystemPrediction(models.Model):
    coinId = models.ForeignKey(Cryptocurrencies, on_delete=models.CASCADE)
    predictedData = models.TextField()
    createdDateTime = models.DateTimeField(auto_now_add=True)
