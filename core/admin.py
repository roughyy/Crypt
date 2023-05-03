from django.contrib import admin

# Register your models here.

from .models import *


admin.site.register(PersonalPrediction)
admin.site.register(UserHistory)
admin.site.register(CoinCategory)
admin.site.register(LSTMModel)
admin.site.register(ProphetScore)
admin.site.register(Cryptocurrencies)
admin.site.register(SystemPrediction)
