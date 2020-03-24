import os
import json

from .custom import send_mass_html_mail
from .models import ImportUser, Course, Comment, Likes, Language, Announcement, LessonStats
from .forms import ImportUserCreationForm, CourseForm, CommentForm, LanguageForm

from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate, login,logout
from django.contrib.sites.shortcuts import get_current_site

from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from math import ceil
from PIL import Image


# Create your views here.

def index(request):
	announcements = Announcement.objects.order_by('-datepost')[0:3]
	announcements_json = []

	for announcement in announcements:
		announcements_json.append(json.dumps(announcement.body))

	context = { 
		'announcements': announcements, 
		'announcements_json' : announcements_json,
		'ann_len': len(announcements)
	}

	return render(request, 'reviewer/index.html', context)


# Admin Views

def admin(request):
	return redirect('admin_dashboard')

def admin_dashboard(request):

	current_page = "dashboard"
	if request.user.is_anonymous:
		return redirect('login')
	else:
		if request.user.is_superuser:
			# Top Users
			topusers = ImportUser.objects.order_by('-exp')[0:5]

			# Language Pref

			lang_stat = {}
			languages = Language.objects.order_by('name')

			for language in languages:
				lang_stat[language.name]= [language.name, language.image.url, '#'+str(language.color), language.importuser_set.all().count()]
				

			# 30 Days Engagement

			dateoftoday = timezone.now()
			last_month = dateoftoday - timedelta(days=30)
			activities = LessonStats.objects.filter(date_made__gt=last_month).order_by('date_made')
			activ_obj = {}
			user_obj = {}
			skip_obj = {}
			mistakes_obj = {}
			activity_date_data = [0] * 30

			if len(activities) == 0:
				activ_obj = None
				user_obj = None
				skip_obj = None
				mistakes_obj = None
			else:
				for activity in activities:

					# Course Data
					if activity.lesson_attr.course.name in activ_obj:
						activ_obj[activity.lesson_attr.course.name] = activ_obj[activity.lesson_attr.course.name]+1
					else:
						activ_obj[activity.lesson_attr.course.name] = 1

					# User Data
					if activity.user_attr in user_obj:
						user_obj[activity.user_attr] = user_obj[activity.user_attr]+1
					else:
						user_obj[activity.user_attr] = 1

					# Skipped Data
					if activity.skips > 0:
						if activity.lesson_attr.id in skip_obj:
							skip_obj[activity.lesson_attr.id] = skip_obj[activity.lesson_attr.id] + activity.skips
						else:
							skip_obj[activity.lesson_attr.id] = activity.skips

					# Mistakes Data
					if activity.mistakes > 0:
						if activity.lesson_attr.id in mistakes_obj:
							mistakes_obj[activity.lesson_attr.id] = mistakes_obj[activity.lesson_attr.id] + activity.mistakes
						else:
							mistakes_obj[activity.lesson_attr.id] = activity.mistakes

					# Full Activity
					diff = 30-(dateoftoday-activity.date_made)
					activity_date_data[diff.days] = activity_date_data[diff.days] + 1

				activ_obj = sorted(activ_obj.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)[0:5]
				user_obj = sorted(user_obj.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)[0:5]
				skip_obj = sorted(skip_obj.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)[0:5]
				mistakes_obj = sorted(mistakes_obj.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)[0:5]


			context = {
				'topusers' : topusers,
				'lang_stat' : lang_stat,
				'course_eng' : activ_obj,
				'active_users' : user_obj,
				'activities' : activity_date_data,
				'skip_data' : skip_obj,
				'mistakes_data' : mistakes_obj,
				'activity_total' : activities.count(),
				'currpage' : current_page
			}

		else:
			context = {'currpage' : current_page}

		return render(request, 'reviewer/admin/dashboard.html', context)

def admin_users(request):

	current_page = "users"
	if request.user.is_anonymous:
		return redirect('login')
	else:
		if request.user.is_superuser:

			users = ImportUser.objects.order_by('username')[0:5]

			if (request.method == "POST"):

				data = request.POST
				confirm = authenticate(username=request.user.username, password=data["password"])
				message = ""

				if confirm == request.user:

					find_uname = ImportUser.objects.get(username=data["username"])
					find_uname.is_superuser = not find_uname.is_superuser
					find_uname.save()

					message = "You have changed " + data["username"] + "'s superuser status."

				else:
					message = "You entered the wrong password."

				context = {
					'users' : users,
					'currpage' : current_page,
					'message' : message
				}


			else:

				context = {
					'users' : users,
					'currpage' : current_page
				}

			return render(request, 'reviewer/admin/users.html', context)

		else:
			context = {'currpage' : current_page}

			return render(request, 'reviewer/admin/users.html', context)


def admin_course_list(request):

	courselist = Course.objects.order_by('code', 'number_len', 'number')
	currpage = "courses"
	
	context = {'courselist': courselist, 'currpage': currpage}
	return render(request, 'reviewer/admin/course-list.html', context)

def admin_course(request, course_id=""):
	return admin_get_course(request, "add", False, "", "")

def admin_course_id(request, course_subj="", course_num ="", purpose="edit"):
	return admin_get_course(request, purpose, False, course_subj, course_num)

def admin_get_course(request, purpose, ajax=True, course_subj="", course_num=""):

	error = None

	referer = request.META['HTTP_REFERER']

	if request.user.is_superuser:
		
		if purpose == "delete":

			del_course = Course.objects.get(code__iexact=course_subj, number__iexact=course_num)
			del_course.delete()

			if "/su/" in referer:
				return redirect('admin_course_list')				
			else:
				return redirect('courselist')
		else:

			if request.method == "POST" and request.user.check_password(request.POST['password']):
				data = request.POST
				courseform = CourseForm(data)

				tempname = data['name'].strip()
				coursefulln = tempname.split(" ")
				tempnum = coursefulln[len(coursefulln)-1]
				tempcode = ' '.join(coursefulln[:-(len(coursefulln)-1)])

				if tempnum.isnumeric():
					temp_oldcurr = data.get('old_curr', False)
					temp_visible = data.get('visible', False)

					if temp_oldcurr == 'on':
						temp_oldcurr = True
					if temp_visible == 'on':
						temp_visible = True
					
					prereq_list = data.getlist('prereq')
					coreq_list = data.getlist('coreq')

					# Add input validation
					if purpose == "add":

						image_uploaded = request.FILES.get('image', None)

						try:
							image_test =  Image.open(image_uploaded)
							image_test.verify()
							
						except:
							image_uploaded = None

						new_course = Course(
							name=data['name'].strip(),
							code=tempcode, 
							number=tempnum, 
							title=data['title'].strip(), 
							description=data['description'.strip()], 
							old_curr=temp_oldcurr, 
							visible=temp_visible,
							image=image_uploaded
							)	

						new_course.save()
						new_course.prereqs.set(Course.objects.filter(id__in=prereq_list))
						new_course.coreqs.set(Course.objects.filter(id__in=coreq_list))
					elif purpose == "edit":

						edit_course = Course.objects.get(code__iexact=course_subj, number__iexact=course_num)

						edit_course.name = data['name'].strip()
						edit_course.code = tempcode
						edit_course.number = tempnum
						edit_course.title = data['title'].strip()
						edit_course.description = data['description'].strip()
						edit_course.old_curr = temp_oldcurr
						edit_course.visible = temp_visible

						image_uploaded = request.FILES.get('image', None)

						try:
							image_test =  Image.open(image_uploaded)
							image_test.verify()
						except:
							image_uploaded = None

						if ((image_uploaded != None) or (data.get('imagehascleared', False) != False )):
							edit_course.image = image_uploaded

						edit_course.lastupdated = timezone.now()
						edit_course.save()
						edit_course.prereqs.set(Course.objects.filter(id__in=prereq_list))
						edit_course.coreqs.set(Course.objects.filter(id__in=coreq_list))

					return redirect('course', tempcode.lower(), tempnum)
				else:
					return redirect('course', tempcode.lower(), tempnum)
			else:
				courselist = Course.objects.filter(visible=True).order_by('code', 'number_len', 'number')


			if purpose == "add":
				courseform = CourseForm()
				context = {'courseform': courseform, 'courses': courselist}
				context['title'] = "Add Course"

			elif purpose == "edit":

				edit_course = Course.objects.get(code__iexact=course_subj, number__iexact=course_num)

				initialvalue = {				
						'name' : edit_course.name,
						'title' : edit_course.title,
						'description' : edit_course.description,
						'old_curr' : edit_course.old_curr,
						'visible' : edit_course.visible
				}

				if edit_course.image:
					initialvalue['image'] = edit_course.image


				courseform = CourseForm(initial=initialvalue)

				getprereqs = []
				getcoreqs = []

				prere =  edit_course.prereqs.all().values_list('id', flat=True)
				core = edit_course.coreqs.all().values_list('id', flat=True)

				for i in prere:		
					getprereqs.append(i)

				for i in core:
					getcoreqs.append(i)

				context = {'courseform': courseform, 'courses': courselist, 'course_subj': edit_course.code.lower(), 
				'course_num': edit_course.number, 'course_prereq': getprereqs, 'course_coreq': getcoreqs}
				context['title'] = "Edit Course"

			if (request.method == "POST") and (request.user.check_password(request.POST['password']) == False):
				context['error'] = "You entered the wrong password."

			if ajax == True:
				return render(request, 'reviewer/courses/course_add.html', context)
			else:	
				context["currpage"] = "courses"
				return render(request, 'reviewer/admin/course_admin.html', context)
		
	else:
		raise HttpResponseForbidden()


def admin_langlist(request):

	langlist = Language.objects.order_by('name')
	currpage = "languages"
	
	context = {'langlist': langlist, 'currpage': currpage}
	return render(request, 'reviewer/admin/language/lang-list.html', context)


def admin_lang_add(request):
	return admin_lang(request, "add", "")

def admin_lang(request, purpose, id=""):

	error = None

	if request.user.is_superuser:
		
		if purpose == "delete":

			del_lang = Language.objects.get(id=id)
			del_lang.delete()

			return redirect('admin_langlist')
		else:

			if request.method == "POST" and request.user.check_password(request.POST['password']):
				data = request.POST

				tempname = data['name']
			
				if len(tempname) > 0:

					image_uploaded = request.FILES.get('image', None)

					try:
						image_test =  Image.open(image_uploaded)
						image_test.verify()
						
					except:
						image_uploaded = None

					# Add input validation
					if purpose == "add":
						new_lang = Language(name=data['name'].strip(), color=data['color'][1:], image=image_uploaded)
						new_lang.save()

					elif purpose == "edit":
						
						edit_lang = Language.objects.get(id=id)

						edit_lang.name = data["name"].strip()
						edit_lang.color = data["color"][1:]
						
						if ((image_uploaded != None) or (data.get('imagehascleared', False) != False )):
							edit_course.image = image_uploaded

						edit_lang.save()


					return redirect('admin_langlist')

				else:
					return redirect(request.META['HTTP_REFERER'])

			else:
				pass

				context = {}
				if purpose == "add":

					langform = LanguageForm(initial= {'color' : '868686'})


					context['langform'] = langform
					context['title'] = "Add Language"
				elif purpose == "edit":
					edit_lang = Language.objects.get(id=id)

					initialvalue = {				
						'name' : edit_lang.name,
						'color' : '#'+edit_lang.color
					}

					if edit_lang.image:
						initialvalue['image'] = edit_lang.image


					langform = LanguageForm(initial=initialvalue)

					context = {'langform': langform, 'edit_lang' : edit_lang }
					context['title'] = "Edit Language"

				if (request.method == "POST") and (request.user.check_password(request.POST['password']) == False):
					context['error'] = "You entered the wrong password."

				context["currpage"] = "languages"
				return render(request, 'reviewer/admin/language/language.html', context)
		
	else:
		raise HttpResponseForbidden()


def admin_announcement(request):

	announcements = Announcement.objects.order_by('-datepost')

	context = {'announcements' : announcements, 'currpage': 'announcements'}

	return render(request, 'reviewer/admin/announcement/announcement-list.html', context)

def admin_announcement_create(request):
	return admin_announcement_update(request, "add", "")

def admin_announcement_update(request, purpose, id=""):

	error = None

	if request.user.is_superuser:
		
		if purpose == "delete":

			del_lang = Language.objects.get(id=id)
			del_lang.delete()

			return redirect('admin_langlist')
		else:

			if request.method == "POST":
				data = request.POST

				bodyjson = json.loads(data["content"])
				notify_users = data.get('em_notif', False)
				temptitle = data.get('title', None)
				bodystring = data.get('bodystring', None)
				retjson = {}

				if temptitle:
					image_uploaded = request.FILES.get('image', None)

					try:
						image_test =  Image.open(image_uploaded)
						image_test.verify()
						
					except:
						image_uploaded = None

					if purpose == "add":
						new_ann = Announcement(
							title=temptitle, 
							body=bodyjson,
							image=image_uploaded,
							poster=request.user
						)
						
						new_ann.save()

						if notify_users:

							domain = get_current_site(request).domain

							settings_url = 'http://'+ domain + reverse('user_settings')

							announcement_url = 'http://'+ domain + reverse('announcement_view', new_ann.id)

							all_users = list(ImportUser.objects.filter(notifications=True).values_list('email', flat=True))
							email_mass = []

							email_from = "Import * Announcement System <" + settings.EMAIL_HOST_USER + ">"

							html_design = render_to_string('reviewer/email/email.html', 
								{
									'settings_url': settings_url,
									'title':	new_ann.title,
									'announcement_url': announcement_url,
									'content': bodystring
							})

							for email in all_users:
								message = (settings.EMAIL_SUBJECT_PREFIX + new_ann.title, 
									bodystring, 
									html_design,
									email_from, 
									[email] )
								email_mass.append(message)

							email_mass = tuple(email_mass)

							send_mass_html_mail(email_mass, fail_silently=False)
							print("Emails sent!")
							print(all_users)


						retjson["redirect_url"] = reverse('announcement_view', new_ann.id)

					elif purpose == "edit":
						
						'''
						edit_lang = Language.objects.get(id=id)

						edit_lang.name = data["name"]
						edit_lang.color = data["color"][1:]
						
						if ((image_uploaded != None) or (data.get('imagehascleared', False) != False )):
							edit_course.image = image_uploaded

						edit_lang.save()
						'''


				return HttpResponse( json.dumps(retjson) )				

			else:

				context = {}
				if purpose == "add":

					context['title'] = "Create Announcement"
				elif purpose == "edit":
					edit_lang = Language.objects.get(id=id)

					initialvalue = {				
						'name' : edit_lang.name,
						'color' : '#'+edit_lang.color
					}

					if edit_lang.image:
						initialvalue['image'] = edit_lang.image


					langform = LanguageForm(initial=initialvalue)

					context = {'langform': langform, 'edit_lang' : edit_lang }
					context['title'] = "Edit Announcement"

				if (request.method == "POST") and (request.user.check_password(request.POST['password']) == False):
					context['error'] = "You entered the wrong password."

				context["currpage"] = "announcements"
				return render(request, 'reviewer/admin/announcement/announcement.html', context)
		
	else:
		raise HttpResponseForbidden()


def announcement_view(request, id):

	announcement = Announcement.objects.get(id=id)

	context = {
		'announcement' : announcement,
		'announcement_json' : json.dumps(announcement.body),

	}


	return render(request, 'reviewer/announcement.html', context)

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

		page_ct = int(ceil(course_commentstotal/page_ct_limit))

		if (cpage > page_ct and page_ct != 0):
			return redirect('course', csubj, cnum)

		else:
			if request.method == "POST":

				data = request.POST
				resultid = None 

				response = redirect('/course/'+csubj+'/'+ str(cnum) + '/c/1', csubj, cnum)

				commentform = CommentForm(data, request.FILES, request=request)

				if request.user.is_authenticated:
					
					image_uploaded = request.FILES.get('image', None)

					try:
						image_test =  Image.open(image_uploaded)
						image_test.verify()
						
					except:
						image_uploaded = None

					# Add input validation
					new_comment = Comment(course_attr=coursefilter[0], user_attr=request.user, body=data['body'], image=image_uploaded)	
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
								'user_url': str(reverse('user', str(last_comment.user_attr.username))),
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
		raise Http404("Course not found.")

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


# User Views

def user_get(request, user_filter, error=None):

	liked_comments = []

	liked_comments_data = []

	if (len(user_filter) > 0):

		user_page_likes = Likes.objects.filter(user_attr=user_filter[0])

		if request.user.is_authenticated:
			user_likes = Likes.objects.filter(user_attr=request.user)
			for i in user_likes:
				liked_comments.append(int(i.comment.id))

		for i in user_page_likes:
			liked_comments_data.append(i.comment)

		liked_comments_data.reverse()

		comments = user_filter[0].comment_set.order_by('-date_posted')
		context = {
			'user_filt': user_filter[0],
			'user_comments':comments , 
			'error': error,
			'liked_comments': str(liked_comments) ,
			'liked_comments_data' : liked_comments_data
		}
		return render(request, 'reviewer/user/user.html', context)
	else:
		raise Http404("User does not exist.")

def user(request, username):

	user_filter = ImportUser.objects.filter(username=username)
	error = None

	if request.method == 'POST':
		if user_filter[0].username == request.user.username:
			utest = ImportUser.objects.get(username=username)

			image_uploaded = request.FILES.get('image', None)

			try:
				image_test =  Image.open(image_uploaded)
				image_test.verify()
				utest.prof_pic = request.FILES.get('image', None)
				utest.save()
			except:
				error = "Upload a valid image file."

		return user_get(request, user_filter, error)
	else:
		return user_get(request, user_filter)
		

def user_settings_uname_is_unique(request, uname):
	retval = False
	filtername = ImportUser.objects.filter(username=uname)
	
	if (len(filtername) == 0 or uname == request.user.username):
		retval = True
	
	return retval


def user_settings(request):

	willRender = True
	error = []

	if request.user.is_authenticated:
		if request.method == 'POST':

			queries = request.GET
			data = request.POST

			unmcheck = queries.get("unamecheck")
			unmcheckbool = (unmcheck == 'y')
			
			if (unmcheckbool):

				unamecheck_callback = {
					'valid': 'n'
				}

				if (data["uname"] == ""):
					unamecheck_callback['valid'] = 'e'
				elif (user_settings_uname_is_unique(request, data["uname"])):
					unamecheck_callback['valid'] = 'y'

					if (data["uname"] == request.user.username):
						unamecheck_callback['valid'] = 's'
				
				response = HttpResponse(json.dumps(unamecheck_callback))

				return response

			elif (queries.get("delete") == 'true'):

				userauth = authenticate(username=request.user.username, password=data.get("password"))
				willRender = False

				if userauth == request.user:
					logout(request)
					userauth.delete()
					return redirect('index')
				else:
					return redirect('user_settings')
			else:

				emptyreqfields = []

				if data["username"] == '':
					emptyreqfields.append("username")
				if data["first_name"] == '':
					emptyreqfields.append("first_name")
				if data["last_name"] == '':
					emptyreqfields.append("last_name")
				if data["e-mail"] == '':
					emptyreqfields.append("e-mail")
				if data["course"] == '':
					emptyreqfields.append("course")

				if len(emptyreqfields) == 0:

					currentuname = request.user.username
		
					currentuser = request.user

					username_valid = user_settings_uname_is_unique(request, data["username"])

					if (username_valid):
						currentuser.username = data["username"]
						currentuser.first_name = data["first_name"]

						if data["middle_name"] == "":
							currentuser.middle_name = None
						else:
							currentuser.middle_name = data["middle_name"]
						

						currentuser.last_name = data["last_name"]
						currentuser.suffix = data["suffix"]

						if data["studentnum"] == "":
							currentuser.studentnum = None
						else:
							currentuser.studentnum = data["studentnum"]

						currentuser.show_studentnum = (data.get("show_studentnum") == 'show')
						currentuser.email = data["e-mail"]
						currentuser.show_email = (data.get("show_email") == 'show')
						currentuser.course = data["course"]

						langvalue = ""

						if data.get("fave_lang", None):
							try:
								currentuser.fave_lang = Language.objects.get(name=data["fave_lang"])
							except Language.DoesNotExist:
								currentuser.fave_lang = None
						else:
							currentuser.fave_lang = None

						currentuser.dark_mode = (data.get("dark_mode") == 'dark')
						currentuser.notifications = (data.get("em_notif") == 'notif_on')
		
						currentuser.save()
						if currentuname != data["username"]:
							try:
								oldUser = ImportUser.objects.get(username=currentuname)
								filename = currentuser.prof_pic.name.split("/")[-1]

								# Image Directory Replace
								media_users_path = os.path.join(settings.MEDIA_ROOT, 'users')
								old_path = os.path.join(media_users_path, currentuname)
								new_path =  os.path.join(media_users_path, data["username"])

								os.rename(old_path, new_path)
								currentuser.prof_pic = 'users/{0}/{1}'.format(data["username"], filename)

								user_page_likes = Likes.objects.filter(user_attr=oldUser)
								user_comments = Comment.objects.filter(user_attr=oldUser)
								user_announcements = Announcement.objects.filter(poster=oldUser)

								for i in user_page_likes:
									i.user_attr = currentuser
									i.save()
								for i in user_comments:
									i.user_attr = currentuser
									i.save()
								for i in user_announcements:
									i.poster = currentuser
									i.save()

								currentuser.save()
								login(request, currentuser)
								oldUser.delete()
							except Exception as e:
								# Atomicity
								currentuser.delete()

								print(e)

						willRender = False

						return redirect('user', request.user.username)
				else:
					error = emptyreqfields

	

		if willRender:

			langlist = Language.objects.all()

			userpassword = request.user.password.split("$")

			userpassword[2] = list(userpassword[2])
			userpassword[3] = list(userpassword[3])

			for i in range(6, len(userpassword[2])):
				userpassword[2][i] = '*'

			for i in range(6, len(userpassword[3])):
				userpassword[3][i] = '*'


			hasEmptyFields = False

			
			if request.user.username == '' or request.user.username == None:
				hasEmptyFields = True
			elif request.user.first_name == '' or request.user.first_name == None:
				hasEmptyFields = True
			elif request.user.last_name == '' or request.user.last_name == None:
				hasEmptyFields = True
			elif request.user.email == '' or request.user.email == None:
				hasEmptyFields = True

			context = {'userpassword_algo' : userpassword[0], 
						'userpassword_iterations': userpassword[1],
						'userpassword_salt' : ''.join(userpassword[2]), 
						'userpassword_hash' : ''.join(userpassword[3]),
						'langlist' : langlist,
						'force_dark_mode' : True,
						'error' : error,
						'emptyfields': hasEmptyFields
						}
			return render(request, 'reviewer/user/user-settings.html', context)
	else:
		return redirect('index')


def user_redirect_info(request):

	usr = request.user

	if usr.is_authenticated and request.method == "POST":
		currURL = request.POST["url"]
		settings_url = reverse('user_settings')

		willRedirect = False

		if (currURL != settings_url):
			if usr.username == '' or usr.username == None:
				willRedirect = True
			elif usr.first_name == '' or usr.first_name == None:
				willRedirect = True
			elif usr.last_name == '' or usr.last_name == None:
				willRedirect = True
			elif usr.email == '' or usr.email == None:
				willRedirect = True

		data = {'field_redirect': willRedirect, 'url_redirect': settings_url }

		return HttpResponse( json.dumps(data) )
	else:
		return Http404()


def register(request):

	langlist = Language.objects.all()

	if request.method == 'POST':
		
		queries = request.GET
		data = request.POST

		unmcheck = queries.get("unamecheck")
		unmcheckbool = (unmcheck == 'y')
		
		if (unmcheckbool):

			unamecheck_callback = {
				'valid': 'n'
			}

			if (data["uname"] == ""):
				unamecheck_callback['valid'] = 'e'
			elif (user_settings_uname_is_unique(request, data["uname"])):
				unamecheck_callback['valid'] = 'y'

				if (data["uname"] == request.user.username):
					unamecheck_callback['valid'] = 's'
			
			response = HttpResponse(json.dumps(unamecheck_callback))

			return response

		else:

			form = ImportUserCreationForm(request.POST)
			if form.is_valid():
				username = form.cleaned_data['username']
				password = form.cleaned_data['password1']
				if (user_settings_uname_is_unique(request, username)):
					form.save()
					user = authenticate(username=username, password=password)

					login(request, user)
					return redirect('user_settings')
				else:
					context = {'form': form, 'langlist' : langlist}
					return render(request, 'registration/register.html', context)
			else:
				context = {'form': form, 'langlist' : langlist}
				return render(request, 'registration/register.html', context)
	else:
		if request.user.is_anonymous:
			form = ImportUserCreationForm()
			context = {'form': form, 'langlist' : langlist}
			return render(request, 'registration/register.html', context)
		else:
			return redirect('login')