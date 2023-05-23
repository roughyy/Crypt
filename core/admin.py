from django.contrib import admin

# Register your models here.

from .models import *


admin.site.register(PersonalPrediction)
admin.site.register(CoinCategory)
admin.site.register(LSTMModel)
admin.site.register(ProphetModel)
admin.site.register(NHitsModel)
admin.site.register(Cryptocurrencies)
