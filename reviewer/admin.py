from django.contrib import admin
from .models import Course, Lesson, Module, Question, ImportUser, Language, Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import ImportUserCreationForm, ImportUserChangeForm

class ImportUserAdmin(UserAdmin):
    add_form = ImportUserCreationForm
    form = ImportUserChangeForm
    model = ImportUser
    list_display = ['username', 'studentnum' , 'email' ]

    fieldsets = (
	(None, {'fields': ('username', 'password', 'exp', 'prof_pic', 'fave_lang')}),
	('Personal Information', {'fields': ('first_name', 'middle_name','last_name', 'suffix', 'studentnum', 'email', 'course')}),
    ('Preferences', {'fields': ('show_studentnum', 'show_email', 'dark_mode')}),
	('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
	)

    readonly_fields =['exp']



admin.site.register(ImportUser, ImportUserAdmin)

# Register your models here.
admin.site.register(Course)
admin.site.register(Comment)
admin.site.register(Lesson)
admin.site.register(Module)
admin.site.register(Question)
admin.site.register(Language)