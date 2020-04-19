import json

from ..custom import *
from ..models import ImportUser, Course, Language, Announcement, LessonStats
from ..forms import CourseForm, LanguageForm, ImportImageForm

from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from io import BytesIO
import mimetypes
from PIL import Image

# Admin Views

def admin(request):
	return redirect('admin_dashboard')

def admin_dashboard(request):

	current_page = "dashboard"
	if request.user.is_anonymous:
		return redirect('login')
	elif request.user.is_superuser:
		# Top Users
		topusers = ImportUser.objects.order_by('-exp')[0:5]

		# Language Pref

		lang_stat = {}
		languages = Language.objects.order_by('name')

		for language in languages:
			lang_stat[language.name]= [language.name,gdrive_import_exportURL()+language.imageID, '#'+str(language.color), language.importuser_set.all().count()]
			
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

		return render(request, 'reviewer/admin/dashboard.html', context)

	else:
		raise PermissionDenied()

def admin_users(request):

	current_page = "users"
	if request.user.is_anonymous:
		return redirect('login')
	elif request.user.is_superuser:
		users = ImportUser.objects.order_by('username')

		if (request.method == "POST"):

			data = request.POST
			confirm = authenticate(username=request.user.username, password=data["password"])
			message = ""

			if confirm == request.user:
				find_uname = ImportUser.objects.filter(username=data["username"]).first()
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
		raise PermissionDenied()

def admin_course_list(request):

	if request.user.is_anonymous:
		return redirect('login')
	elif request.user.is_superuser:
		courselist = Course.objects.order_by('code', 'number_len', 'number')
		currpage = "courses"
		context = {'courselist': courselist, 'currpage': currpage}

		return render(request, 'reviewer/admin/course-list.html', context)
	else:
		raise PermissionDenied()

def admin_course(request, course_id=""):
	return admin_get_course(request, "add", "", "")

def admin_course_id(request, course_subj="", course_num ="", purpose="edit"):
	return admin_get_course(request, purpose, course_subj, course_num)

def admin_get_course(request, purpose, course_subj="", course_num=""):

	referer = request.META.get('HTTP_REFERER', "")

	if request.user.is_anonymous:
		return redirect('login')
	elif request.user.is_superuser:
		if purpose == "delete":
			del_course = Course.objects.filter(code__iexact=course_subj, number__iexact=course_num).first()

			for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
				try:
					service = gdrive_connect()
					reffolder = 'references/{}'.format(del_course.name)
					reffolder = gdrive_traverse_path(service, path=reffolder, create=True)
					gdrive_delete_file(service, reffolder['id'])
					gdrive_delete_file(service, del_course.imageID)
					break
				except Exception as e:
					if settings.DEBUG: print(e)

			del_course.delete()

			return redirect( 'admin_course_list' if "/su/" in referer else 'courselist' )				

		elif request.method == "POST" and request.user.check_password(request.POST['password']):

			data = request.POST

			tempname = data['name'].strip()
			coursefulln = tempname.split(" ")
			tempnum = coursefulln[-1]
			tempcode = ' '.join(coursefulln[:-1])
			
			if tempnum.isnumeric():
				temp_oldcurr, temp_visible = (data.get('old_curr', False) == 'on'), (data.get('visible', False) == 'on')		
				prereq_list, coreq_list = data.getlist('prereq'), data.getlist('coreq')

				image_uploaded = request.FILES.get('image', None)
				image_uploadedID = None
				service = None

				try:
					image_test =  Image.open(image_uploaded)
					image_test.verify()

					image_test =  Image.open(image_uploaded)
					image_mime = mimetypes.guess_type(str(image_uploaded))[0]

					image_test.thumbnail((600,600))
					image_bytes = BytesIO()
					image_test.save(image_bytes, format=image_test.format)

					for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
						try:
							service = gdrive_connect()
							coursefolder = 'media/course/{}'.format(tempname)
							coursefolder = gdrive_traverse_path(service, path=coursefolder, create=True)

							metadata = {'name': str(image_uploaded), 'parents': [coursefolder['id']] }
							image_uploadedID = gdrive_upload_bytes_tofile(service, image_bytes, metadata, image_mime)
							break
						except Exception as e:
							if settings.DEBUG: print(e)
				except:
					pass
					
				if purpose == "add":	
					course = Course(
						name=data['name'].strip(),
						code=tempcode, 
						number=tempnum, 
						title=data['title'].strip(), 
						description=data['description'.strip()], 
						old_curr=temp_oldcurr, 
						visible=temp_visible,
						imageID=image_uploadedID
					)
				elif purpose == "edit":

					course = Course.objects.filter(code__iexact=course_subj, number__iexact=course_num).first()

					course.name = data['name'].strip()
					course.code = tempcode
					course.number = tempnum
					course.title = data['title'].strip()
					course.description = data['description'].strip()
					course.old_curr = temp_oldcurr
					course.visible = temp_visible
					course.lastupdated = timezone.now()

					oldphotoID = course.imageID
					
					if image_uploaded or data.get('imagehascleared', False):
						course.imageID = image_uploadedID
						if oldphotoID: gdrive_delete_file(service, oldphotoID)

				course.save()
				course.prereqs.set(Course.objects.filter(id__in=prereq_list))
				course.coreqs.set(Course.objects.filter(id__in=coreq_list))

			return redirect('course', tempcode.lower(), tempnum)
			
		else:
			courselist = Course.objects.filter(visible=True).order_by('code', 'number_len', 'number')

			if purpose == "add":
				courseform = CourseForm()
				context = { 'courseform': courseform, 
							'courses': courselist,
							'title': "Add Course"
						}

			elif purpose == "edit":

				edit_course = Course.objects.filter(code__iexact=course_subj, number__iexact=course_num).first()

				initialvalue = {				
						'name' : edit_course.name,
						'title' : edit_course.title,
						'description' : edit_course.description,
						'old_curr' : edit_course.old_curr,
						'visible' : edit_course.visible
				}

				if edit_course.imageID:
					initialvalue['imageID'] = gdrive_import_exportURL()+edit_course.imageID

				courseform = CourseForm(initial=initialvalue)

				getprereqs, getcoreqs = list(edit_course.prereqs.all().values_list('id', flat=True)), list(edit_course.coreqs.all().values_list('id', flat=True))

				context = { 'courseform': courseform, 
							'courses': courselist, 
							'course_subj': edit_course.code.lower(), 
							'course_num': edit_course.number, 
							'course_prereq': getprereqs, 
							'course_coreq': getcoreqs,
							'title' : "Edit Course"
						}

			if (request.method == "POST") and (request.user.check_password(request.POST['password']) == False):
				context['error'] = "You entered the wrong password."

			if request.is_ajax():
				return render(request, 'reviewer/courses/course_add.html', context)
			else:	
				context["currpage"] = "courses"
				return render(request, 'reviewer/admin/course_admin.html', context)
	
	else:
		raise PermissionDenied()


def admin_langlist(request):

	if request.user.is_anonymous:
		return redirect('login')
	elif request.user.is_superuser:
		langlist = Language.objects.order_by('name')
		currpage = "languages"
		
		context = {'langlist': langlist, 'currpage': currpage}
		return render(request, 'reviewer/admin/language/lang-list.html', context)
	else:
		raise PermissionDenied()

def admin_lang_add(request):
	return admin_lang(request, "add", "")

def admin_lang(request, purpose, id=""):

	error = None

	if request.user.is_anonymous:
		return redirect('login')
	elif request.user.is_superuser:
		
		if purpose == "delete":
			del_lang = Language.objects.filter(id=id).first()
			for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
				try:
					service = gdrive_connect()
					langfolder = 'media/lang/{}'.format(del_course.name)
					langfolder = gdrive_traverse_path(service, path=langfolder, create=True)
					gdrive_delete_file(service, langfolder['id'])
					break
				except Exception as e:
					if settings.DEBUG: print(e)

			del_lang.delete()

			return redirect('admin_langlist')
		else:
			if request.method == "POST" and request.user.check_password(request.POST['password']):
				data = request.POST
				tempname = data['name']
			
				if len(tempname) > 0:
					image_uploaded = request.FILES.get('image', None)
					image_uploadedID = None

					try:	
						image_test =  Image.open(image_uploaded)
						image_test.verify()

						image_test =  Image.open(image_uploaded)
						image_mime = mimetypes.guess_type(str(image_uploaded))[0]

						image_test.thumbnail((400,400))
						image_bytes = BytesIO()
						image_test.save(image_bytes, format=image_test.format)

						for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
							try:
								service = gdrive_connect()
								langfolder = 'media/lang/{}'.format(data['name'].strip())
								langfolder = gdrive_traverse_path(service, path=langfolder, create=True)

								metadata = {'name': '{}.{}'.format(data['name'].strip(), image_test.format), 'parents': [langfolder['id']] }
								image_uploadedID = gdrive_upload_bytes_tofile(service, image_bytes, metadata, image_mime)
								break
							except Exception as e:
								if settings.DEBUG: print(e)
					except:
						pass

					# Add input validation
					if purpose == "add":
						Language.objects.create(name=data['name'].strip(), color=data['color'][1:], imageID=image_uploadedID)
					elif purpose == "edit":
						
						edit_lang = Language.objects.filter(id=id).first()
						edit_lang.name = data["name"].strip()
						edit_lang.color = data["color"][1:]
						oldphotoID = edit_lang.imageID
						
						if image_uploaded or data.get('imagehascleared', False):
							edit_lang.imageID = image_uploadedID
							if oldphotoID: gdrive_delete_file(service, oldphotoID)
						edit_lang.save()

					return redirect('admin_langlist')
				else:
					return redirect(request.META['HTTP_REFERER'])
			else:
				context = {}
				if purpose == "add":
					langform = LanguageForm(initial= {'color' : '868686'})

					context['langform'] = langform
					context['title'] = "Add Language"
				elif purpose == "edit":
					edit_lang = Language.objects.filter(id=id).first()
					initialvalue = {				
						'name' : edit_lang.name,
						'color' : '#'+edit_lang.color
					}

					if edit_lang.imageID:
						initialvalue['imageID'] = gdrive_import_exportURL()+edit_lang.imageID

					langform = LanguageForm(initial=initialvalue)

					context = {'langform': langform, 'edit_lang' : edit_lang }
					context['title'] = "Edit Language"

				if (request.method == "POST") and (request.user.check_password(request.POST['password']) == False):
					context['error'] = "You entered the wrong password."

				context["currpage"] = "languages"
				return render(request, 'reviewer/admin/language/language.html', context)
	else:
		raise PermissionDenied()

def admin_announcement(request):

	if request.user.is_anonymous:
		return redirect('login')
	elif request.user.is_superuser:
		announcements = Announcement.objects.order_by('-datepost')
		context = {'announcements' : announcements, 'currpage': 'announcements'}
		return render(request, 'reviewer/admin/announcement/announcement-list.html', context)
	else:
		raise PermissionDenied()

def admin_announcement_create(request):
	return admin_announcement_update(request, "add", "")

def admin_announcement_update(request, purpose, id=""):

	error = None

	if request.user.is_anonymous:
		return redirect('login')
	elif request.user.is_superuser:
		if purpose == "delete":
			del_ann = Announcement.objects.filter(id=id).first()
			del_ann.delete()

			return redirect('admin_announcement')
		elif request.method == "POST":
			data = request.POST

			bodyjson = json.loads(data["content"])
			notify_users = data.get('em_notif', False)
			temptitle = data.get('title', None).strip()
			bodystring = data.get('bodystring', None).strip()
			retjson = {}

			if temptitle:
				image_uploaded = request.FILES.get('image', None)
				image_uploadedID = None

				try:	
					image_test =  Image.open(image_uploaded)
					image_test.verify()

					image_test =  Image.open(image_uploaded)
					image_mime = mimetypes.guess_type(str(image_uploaded))[0]

					image_test.thumbnail((1000,1000))
					image_bytes = BytesIO()
					image_test.save(image_bytes, format=image_test.format)

					for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
						try:
							service = gdrive_connect()
							langfolder = 'media/announcements'
							langfolder = gdrive_traverse_path(service, path=langfolder, create=True)

							metadata = {'name': str(image_uploaded), 'parents': [langfolder['id']] }
							image_uploadedID = gdrive_upload_bytes_tofile(service, image_bytes, metadata, image_mime)
							break
						except Exception as e:
							if settings.DEBUG: print(e)
				except:
					pass

				if purpose == "add":
					new_ann = Announcement.objects.create(title=temptitle, body=bodyjson, imageID=image_uploadedID, poster=request.user)
				
					if notify_users:

						all_users = list(ImportUser.objects.filter(notifications=True).values_list('email', flat=True))
						email_mass = []

						if len(all_users) > 0:

							domain = get_current_site(request).domain
							settings_url = 'http://'+ str(domain) + reverse('user_settings') 
							announcement_url = 'http://'+ str(domain) + reverse('announcement_view', args=[str(new_ann.id)])

							email_from = "Import * Announcement System <{}>".format(settings.EMAIL_HOST_USER)

							html_design = render_to_string('reviewer/email/email.html', 
								{
									'settings_url': settings_url,
									'title': new_ann.title,
									'announcement_url': announcement_url,
									'content': bodystring
							})

							for email in all_users:
								message = (settings.EMAIL_SUBJECT_PREFIX + new_ann.title, bodystring, html_design, email_from, [email] )
								email_mass.append(message)

							send_mass_html_mail( tuple(email_mass), fail_silently=False)

							if settings.DEBUG:
								print("Emails sent!")
								print(all_users)

					retjson["redirect_url"] = reverse('announcement_view', args=[str(new_ann.id)])
					
				elif purpose == "edit":
					
					edit_ann = Announcement.objects.filter(id=id).first()

					edit_ann.title = temptitle
					edit_ann.body = bodyjson
					
					oldphotoID = edit_ann.imageID
					
					if image_uploaded or data.get('imagehascleared', False):
						edit_ann.imageID = image_uploadedID
						if oldphotoID: gdrive_delete_file(service, oldphotoID)

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
				edit_ann = Announcement.objects.filter(id=id).first()
				edit_ann_json = json.dumps(edit_ann.body)

				initialvalue = {}

				if edit_ann.imageID:
					initialvalue['imageID'] = edit_ann.imageID

				image_form = ImportImageForm(initial=initialvalue)

				context = {
					'edit_ann': edit_ann, 
					'edit_ann_json': edit_ann_json,
					'image_form': image_form
				}
				context['title'] = "Edit Announcement"

			context["currpage"] = "announcements"
			return render(request, 'reviewer/admin/announcement/announcement.html', context)
	else:
		raise PermissionDenied()

