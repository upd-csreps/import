from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.construction, name="construction"),
    path('home', views.index, name="index"),
    path('course/', views.courselist, name="courselist"),
    path('course/<str:csubj>/<int:cnum>', views.course, name="course"),
    re_path(r'^course/(?P<csubj>[a-zA-Z]+)/(?P<cnum>[0-9]+)/($|(?P<catchar>[c,l,r])/(?P<cpage>[0-9]*)$)', views.coursecpage, name="coursecpage"),
    path('su', views.su, name="su"),
    path('u/register', views.register, name="register"),
    path('u/*/<str:username>', views.user, name="user"),
]
