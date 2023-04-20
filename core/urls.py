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
]
