from django.urls import path
from . import views

urlpatterns = [
    path('', views.construction, name="construction"),
    path('home', views.index, name="index"),
]
