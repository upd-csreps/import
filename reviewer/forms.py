from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ImportUser, Course


# Copy from models.py
class CourseForm(forms.Form):

	query = Course.objects.order_by('code', 'number_len', 'number')

	name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'ex. CS 11', 'autocomplete': 'off'}))
	code = forms.CharField(max_length=10)
	number = forms.CharField(max_length=10)
	title = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'ex. Computer Programming I', 'autocomplete': 'off'}))
	description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder' : '', 'rows': 4}), required=False)
	old_curr = forms.BooleanField(widget=forms.CheckboxInput(attrs={ 'class': 'form-check-input' }), required=False, initial=False)
	visible = forms.BooleanField(widget=forms.CheckboxInput(attrs={ 'class': 'form-check-input' }), required=False, initial=True)
	imagehascleared = forms.BooleanField(widget=forms.CheckboxInput(attrs={ 'class': 'form-check-input' }), required=False,initial=False)
	lastupdated = timezone.now()
	image = forms.ImageField(required=False)


	prereq = forms.ModelMultipleChoiceField(
		widget = forms.CheckboxSelectMultiple(),
        queryset = query,
        required = False
	)
	coreq = forms.ModelMultipleChoiceField(
		widget = forms.CheckboxSelectMultiple(),
        queryset = query,
        required = False
	)

class CommentForm(forms.Form):
	
	date_posted = timezone.now()

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop("request")
		user = self.request.user
		super(CommentForm, self).__init__(*args, **kwargs)

		disabled = True

		if user.is_anonymous:
			attributes = {
			'class': 'form-control -disabled', 
			'placeholder' : 'You must be logged in to comment.', 
			'readonly':'readonly'
			}
			
		else:
			attributes = { 
			'class': 'form-control comment-text-area', 
			'placeholder' : 'Comment', 
			'autocomplete': 'off'
			}
			disabled = False

		self.fields['body'] = forms.CharField(max_length=150, widget=forms.Textarea(attrs=attributes))
		self.fields['image'] = forms.ImageField(required=False, disabled=disabled)


class ImportUserCreationForm(UserCreationForm):

	class Meta(UserCreationForm):
		model = ImportUser
		fields = ('username', 'first_name', 'middle_name', 'last_name', 'suffix', 'studentnum', 'show_studentnum', 'email', 'show_email', 'course', 'fave_lang')

class ImportUserChangeForm(UserChangeForm):

    class Meta:
        model = ImportUser
        fields = ('username', 'first_name', 'middle_name', 'last_name', 'suffix', 'studentnum', 'show_studentnum', 'email', 'show_email', 'course', 'fave_lang', 'dark_mode')

class LanguageForm(forms.Form):

	name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
	image = forms.ImageField(required=False)
	imagehascleared = forms.BooleanField(widget=forms.CheckboxInput(attrs={ 'class': 'form-check-input' }), required=False,initial=False)
	color = forms.CharField(max_length=7, widget=forms.TextInput(attrs={'class': 'color-picker', 'autocomplete': 'off'}))
	