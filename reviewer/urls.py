from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('course/', views.courselist, name="courselist"),
    path('course/<str:csubj>/<int:cnum>/', views.course, name="course"),
    re_path(r'^course/(?P<csubj>[a-zA-Z]+)/(?P<cnum>[0-9]+)/($|(?P<catchar>[c,l,r])/(?P<cpage>[0-9]*)$)', views.coursecpage, name="coursecpage"),
    path('course/<str:csubj>/<int:cnum>/like-comment/', views.comment_like, name="comment_like"),
    path('su/', views.admin , name="admin"),
    path('su/dashboard', views.admin_dashboard , name="admin_dashboard"),
    path('su/users', views.admin_users , name="admin_users"),
    path('su/course/<str:purpose>/get/', views.admin_get_course, name="admin_get_course"),
    path('su/course/<str:purpose>/<str:course_subj>/<str:course_num>', views.admin_course_id, name="admin_course_id"),
    path('su/course/<str:purpose>/', views.admin_course, name="admin_course"),
    path('u/register/', views.register, name="register"),
    path('u/settings/', views.user_settings, name="user_settings"),
    path('u/*/<str:username>/', views.user, name="user"),
]
