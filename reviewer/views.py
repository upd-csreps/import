from django.shortcuts import render, redirect

from .models import Course, Announcement
from .forms import CourseForm

# Create your views here.

def index(request):
	announcements = Announcement.objects.order_by('datepost')

	context = {'announcements': announcements, 'ann_len': len(announcements)}

	return render(request, 'reviewer/index.html', context)

def construction(request):
	return render(request, 'reviewer/construction.html')

def su(request):


	courses = Course.objects.order_by('name')

	if request.method == "POST":
		data = request.POST
		courseform = CourseForm(data)

		tempname = data['name']
		coursefulln = tempname.split(" ")
		tempnum = coursefulln[len(coursefulln)-1]
		tempcode = ' '.join(coursefulln[:-(len(coursefulln)-1)])
		temp_oldcurr = data.get('old_curr', False)
		temp_visible = data.get('visible', True)

		if temp_oldcurr == 'on':
			temp_oldcurr = True
		if temp_visible == 'on':
			temp_visible = True
		
		# Add input validation
		new_course = Course(name=data['name'], code=tempcode, number=tempnum, title=data['title'], description=data['description'], old_curr=temp_oldcurr, visible=temp_visible)	

		new_course.save()
		return redirect('su')
	else:
		courseform = CourseForm()
	
	context = { 'courses': courses, 'courseform': courseform}


	return render(request, 'reviewer/admin.html', context)


def course(request, csubj, cnum):

	coursefilter = Course.objects.filter(code__iexact=csubj).filter(number__iexact=str(cnum))

	context = {'course_filt': coursefilter[0]}
	return render(request, 'reviewer/course.html', context)