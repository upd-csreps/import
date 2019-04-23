from django.contrib import admin
from .models import Course, User, Lesson, Module, Question

# Register your models here.
admin.site.register(Course)
admin.site.register(User)
admin.site.register(Lesson)
admin.site.register(Module)
admin.site.register(Question)