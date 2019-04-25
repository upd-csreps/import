from django.urls import path
from . import views

urlpatterns = [
    path('', views.construction, name="construction"),
    path('home', views.index, name="index"),
    path('course/<str:csubj>/<int:cnum>', views.course, name="course"),
    path('su', views.su, name="su"),
]
