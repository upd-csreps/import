from django import forms

# Copy from models.py
class CourseForm(forms.Form):

	name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'Course Code & No.'}))
	code = forms.CharField(max_length=10)
	number = forms.CharField(max_length=10)
	title = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'Title'}))
	description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder' : 'Description'}), required=False)
	old_curr = forms.BooleanField(widget=forms.CheckboxInput(attrs={ 'class': 'form-check-input' }), required=False, initial=False)