from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class PersonalPrediction(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    predictedData = models.TextField(null=True)
    createdDateTime = models.DateTimeField(auto_now_add=True, null=True)


class UserHistory(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    predictionId = models.ForeignKey(PersonalPrediction, on_delete=models.CASCADE)


class CoinCategory(models.Model):
    CATEGORY = (
        ("StableCoin", "Stable Coin"),
        ("Metaverse", "Metaverse Coin"),
        ("Regular", "Regular Coin"),
        ("Defi", "Defi Coin"),
        ("SolanaNetwork", "Solana Network Coin"),
        ("BNBchain", "BNB Chain Coin"),
    )
    category = models.CharField(max_length=50, null=True, choices=CATEGORY)


class MachineLearningModel(models.Model):
    rmse = models.CharField(max_length=20)
    mape = models.CharField(max_length=20)
    updateDateTime = models.DateTimeField(auto_now_add=True)


class Cryptocurrencies(models.Model):
    coinName = models.CharField(max_length=30)
    symbol = models.CharField(max_length=10)
    categoryId = models.ForeignKey(CoinCategory, on_delete=models.CASCADE)
    lastPrice = models.CharField(max_length=30)
    historicalData = models.TextField()
    modelId = models.ForeignKey(MachineLearningModel, on_delete=models.CASCADE)
    updateDateTime = models.DateTimeField(auto_now_add=True)


class SystemPrediction(models.Model):
    coinId = models.ForeignKey(Cryptocurrencies, on_delete=models.CASCADE)
    predictedData = models.TextField()
    createdDateTime = models.DateTimeField(auto_now_add=True)
