from django.shortcuts import render, redirect

from .models import Course
from .forms import CourseForm

# Create your views here.

def index(request):

	courses = Course.objects.order_by('name')

	if request.method == "POST":
		data = request.POST
		courseform = CourseForm(data)

		tempname = data['name']
		coursefulln = tempname.split(" ")
		tempnum = coursefulln[len(coursefulln)-1]
		tempcode = ' '.join(coursefulln[:-(len(coursefulln)-1)])
		
		# Add input validation
		new_course = Course(name=data['name'], code=tempcode, number=tempnum, title=data['title'], description=data['description'], old_curr=data.get('old_curr', False))
		new_course.save()
		return redirect('index')
	else:
		courseform = CourseForm()
	
	context = { 'courses': courses, 'courseform': courseform}

	return render(request, 'reviewer/index.html', context)

def construction(request):
	return render(request, 'reviewer/construction.html')