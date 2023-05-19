from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("detail/", views.detail, name="detail"),
    path("search/", views.search, name="search"),
    path("upload/", views.upload, name="upload"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logoutUser, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("result/", views.result, name="result"),
    path(
        "pastPrediction/<int:personal_prediction_id>/",
        views.pastPrediction,
        name="pastPrediction",
    ),
    path("404/<message>", views.PageNotFound, name="404"),
    path(
        "CustomPrediction/<int:personal_prediction_id>/",
        views.CustomPrediction,
        name="CustomPrediction",
    ),
    path("debug/", views.debug, name="debug"),
    path(
        "populate-cryptocurrencies-data/",
        views.populateCryptocurrenciesData,
        name="populate-cryptocurrencies-data",
    ),
    path(
        "populate-cryptocurrencies-historical-data/",
        views.populateCryptocurrenciesHistoricalData,
        name="populate-cryptocurrencies-historical-data",
    ),
]
