from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login

from django.http import Http404, HttpResponse
from django.contrib.auth import get_user_model
from .models import Course, Announcement, ImportUser, Comment, Likes
from .forms import CourseForm, CommentForm, CommentFormDisabled, ImportUserCreationForm
import math
import json

# Create your views here.

def index(request):
	announcements = Announcement.objects.order_by('datepost')

	context = {'announcements': announcements, 'ann_len': len(announcements)}

	return render(request, 'reviewer/index.html', context)

def construction(request):
	return render(request, 'reviewer/construction.html')

def course_add(request):

	if request.user.is_superuser:
		

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
			return redirect('course_add')
		else:
			courseform = CourseForm()
		
		context = {'courseform': courseform}


		return render(request, 'reviewer/admin.html', context)
	else:
		return


def courselist(request):

	courselist = Course.objects.filter(visible=True).order_by('code', 'number_len', 'number')

	context = {'courselist': courselist, 'course_count': len(courselist)}
	return render(request, 'reviewer/courses/course-list.html', context)

def course(request, csubj, cnum):
	return coursecpage( request, csubj, cnum, 'l', '1')

def coursecpage(request, csubj, cnum, catchar = 'l', cpage = 1):

	if (catchar == None):
		catchar = "l"
		cpage = 1

	if (cpage == ""):
		cpage = 1

	cpage = int(cpage)
	page_ct_limit = 10	

	coursefilter = Course.objects.filter(code__iexact=csubj).filter(number__iexact=str(cnum))

	if (len(coursefilter) > 0):
		if (cpage < 1):
			cpage = 1

		startindex = (cpage - 1)*page_ct_limit
		course_comments_filtered = coursefilter[0].comment_set.order_by('-date_posted')[startindex:startindex+page_ct_limit]
		course_commentstotal = len(coursefilter[0].comment_set.order_by('-date_posted'))

		page_ct = int(math.ceil(course_commentstotal/page_ct_limit))

		if (cpage > page_ct):
			return redirect('course', csubj, cnum)

		else:
			if request.method == "POST":

				data = request.POST
				resultid = None 

				response = redirect('/course/'+csubj+'/'+ str(cnum) + '/c/1', csubj, cnum)

				commentform = CommentForm(data, request.FILES, request=request)

				if request.user.is_authenticated:
					
					# Add input validation
					new_comment = Comment(course_attr=coursefilter[0], user_attr=request.user, body=data['body'], image=request.FILES.get('image', None))	
					new_comment.save()
					resultid = new_comment.id

					if cpage == 1:
						data = {'commentid': resultid}
						if new_comment.image:
							data['image'] =  new_comment.image.url
						response = HttpResponse( json.dumps(data) )

				return response

			elif request.method == "DELETE":

				comment_findid = int(request.body.decode("utf-8").split("-")[1])

				delcom = Comment.objects.get(pk=comment_findid)
				result = {}
				if (request.user == delcom.user_attr):
					delcom.delete()

					try:
						last_comment = coursefilter[0].comment_set.order_by('-date_posted')[startindex+page_ct_limit-1]

						likedstat = last_comment.likes_set.filter(user_attr=request.user).exists()

						if last_comment:
							result = { 
								'id': str(last_comment.id),
								'user' : str(last_comment.user_attr.username),
								'body' : str(last_comment.body),
								'date' : str(last_comment.date_posted),
								'liked' : likedstat,
								'like_ct' : len(last_comment.likes_set.all())
							 }

							if last_comment.image:
								result["image"]	= str(last_comment.image.url)
							if last_comment.user_attr.prof_pic:
								result['user_img'] = str(last_comment.user_attr.prof_pic.url),
					except IndexError:
						pass

				return HttpResponse(json.dumps(result))

			elif request.method == "GET":

				liked_comments = []

				commentform = CommentForm(auto_id="comment-form", request=request)

				if request.user.is_authenticated:
					

					user_likes = Likes.objects.filter(user_attr=request.user)

					for i in user_likes:
						liked_comments.append(int(i.comment.id))


				context = {
						'course_filt': coursefilter[0],
						'course_comment_count': course_commentstotal,
						'course_comments': course_comments_filtered,
						'comment_form': commentform,
						'liked_comments': str(liked_comments),
						'section': catchar,
						'page_count' : page_ct,
						'cpage' : cpage,
						'prev_page' : cpage-1,
						'next_page' : cpage+1
						}
				return render(request, 'reviewer/courses/course.html', context)
	else:
		raise Http404("You do not have enough permission for this page")



def comment_like(request, csubj, cnum):

	if request.method == "POST":

		data = request.POST
		resultid = None 

		response = redirect('/course/'+csubj+'/'+ str(cnum) + '/c/1', csubj, cnum)

		if request.user.is_authenticated:

			comment_findid = int(request.body.decode("utf-8").split("-")[1])
			comm_like = Comment.objects.get(pk=comment_findid)	

			like_state = Likes.objects.filter(comment=comm_like, user_attr=request.user)

			if like_state.exists():
				like_state.delete()
				like_state = False

			else:
				new_like = Likes(comment=comm_like, user_attr=request.user)	
				new_like.save()
				like_state = True

			like_count_callback = {
				'count': len(comm_like.likes_set.all()), 
				'state': like_state
			}

			response = HttpResponse(json.dumps(like_count_callback))

		return response


def user(request, username):

	user_filter = ImportUser.objects.filter(username=username)

	if (len(user_filter) > 0):
		comments = user_filter[0].comment_set.order_by('-date_posted')
		context = {'user_filt': user_filter[0], 'user_comments':comments }
		return render(request, 'reviewer/user.html', context)
	else:
		raise Http404("User does not exist.")



def register(request):
	
	if request.method == 'POST':
		form = ImportUserCreationForm(request.POST)

		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)

			login(request, user)
			return redirect('index')
	else:
		form = ImportUserCreationForm()

	context = {'form': form}
	return render(request, 'registration/register.html', context)