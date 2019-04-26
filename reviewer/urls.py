from django.urls import path
from . import views

urlpatterns = [
    path('', views.construction, name="construction"),
    path('home', views.index, name="index"),
    path('course/', views.courselist, name="courselist"),
    path('course/<str:csubj>/<int:cnum>', views.course, name="course"),
    path('su', views.su, name="su"),
    path('u/register', views.register, name="register"),
    path('u/<str:username>', views.user, name="user"),
]
