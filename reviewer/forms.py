from django import forms
import datetime
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ImportUser

# Copy from models.py
class CourseForm(forms.Form):

	name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'Course Code & No.'}))
	code = forms.CharField(max_length=10)
	number = forms.CharField(max_length=10)
	title = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'Title'}))
	description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder' : 'Description'}), required=False)
	old_curr = forms.BooleanField(widget=forms.CheckboxInput(attrs={ 'class': 'form-check-input' }), required=False, initial=False)
	visible = forms.BooleanField(widget=forms.CheckboxInput(attrs={ 'class': 'form-check-input' }), required=False, initial=True)
	lastupdated = datetime.datetime.now()

class CommentForm(forms.Form):

	body = forms.CharField(max_length=150, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder' : 'Comment'}))
	image = forms.FileField(required=False)
	date_posted = datetime.datetime.now()

class ImportUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = ImportUser
        fields = ('username', 'first_name', 'last_name', 'suffix', 'studentnum', 'email', 'course', 'fave_lang')

class ImportUserChangeForm(UserChangeForm):

    class Meta:
        model = ImportUser
        fields = ('username', 'first_name', 'last_name', 'suffix', 'studentnum', 'email', 'course')