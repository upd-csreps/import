import json

from ..custom import send_mass_html_mail
from ..models import ImportUser, Course, Language, Announcement, LessonStats
from ..forms import CourseForm, LanguageForm, ImportImageForm

from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site

from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from PIL import Image

from googleapiclient.discovery import build
from google.oauth2 import service_account


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
			LessonStats.objects.filter(date_made__lte=last_month).delete()

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
							edit_lang.image = image_uploaded

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

			del_ann = Announcement.objects.get(id=id)
			del_ann.delete()

			return redirect('admin_announcement')
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

							all_users = list(ImportUser.objects.filter(notifications=True).values_list('email', flat=True))
							email_mass = []

							if len(all_users) > 0:

								domain = get_current_site(request).domain
								settings_url = 'http://'+ str(domain) + reverse('user_settings') 
								announcement_url = 'http://'+ str(domain) + reverse('announcement_view', args=[str(new_ann.id)])

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

						retjson["redirect_url"] = reverse('announcement_view', args=[str(new_ann.id)])
						
					elif purpose == "edit":
						
						edit_ann = Announcement.objects.get(id=id)

						edit_ann.title = temptitle
						edit_ann.body = bodyjson
						
						if ((image_uploaded != None) or (data.get('imagehascleared', False) != False )):
							edit_ann.image = image_uploaded

						edit_ann.save()

						retjson["redirect_url"] = reverse('announcement_view', args=[str(edit_ann.id)])

					retjson["status"] = "success"
		
				else:
					retjson["status"] = "fail"	

				return JsonResponse(retjson)
							

			else:

				context = {}
				if purpose == "add":
					context['title'] = "Create Announcement"
				elif purpose == "edit":
					edit_ann = Announcement.objects.get(id=id)
					edit_ann_json = json.dumps(edit_ann.body)

					initialvalue = {}

					if edit_ann.image:
						initialvalue['image'] = edit_ann.image


					image_form = ImportImageForm(initial=initialvalue)


					context = {
						'edit_ann': edit_ann, 
						'edit_ann_json': edit_ann_json,
						'image_form': image_form}
					context['title'] = "Edit Announcement"

				context["currpage"] = "announcements"
				return render(request, 'reviewer/admin/announcement/announcement.html', context)
		
	else:
		raise HttpResponseForbidden()

