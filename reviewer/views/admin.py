import json

from ..custom import *
from ..models import (ImportUser, Course, 
	Language, Announcement, Lesson, Question, LessonStats)
from ..forms import CourseForm, LanguageForm, ImportImageForm

from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied

from django.http import Http404, JsonResponse
from django.db.models import F
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from io import BytesIO
import mimetypes
from PIL import Image

# Admin Views

@login_required
def admin(request):
	return redirect('admin_dashboard')

@login_required
def admin_dashboard(request):
	current_page = "dashboard"
	if request.user.is_superuser:
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

@login_required
def admin_announcement(request):
	if request.user.is_superuser:
		announcements = Announcement.objects.order_by('-datepost')
		context = {'announcements' : announcements, 'currpage': 'announcements'}
		return render(request, 'reviewer/admin/announcement/announcement-list.html', context)
	else:
		raise PermissionDenied()

@login_required
def admin_announcement_create(request):
	return admin_announcement_update(request, "add", "")

@login_required
def admin_announcement_update(request, purpose, id=""):

	purpose = purpose.lower()

	allowed_purpose = ['add', 'edit','delete']
	if purpose not in allowed_purpose:
		raise Http404()

	error = None

	if request.user.is_superuser:
		if purpose == allowed_purpose[2]:
			del_ann = Announcement.objects.filter(id=id).first()
			del_ann.delete()

			return redirect('admin_announcement')
		elif request.method == "POST":
			data = request.POST

			bodyjson = json.loads(data["content"])
			notify_users = data.get('em_notif', False)
			temptitle = data.get('title', None)

			if temptitle:
				temptitle = temptitle.strip()

			bodystring = data.get('bodystring', None)

			if bodystring:
				temptitle = temptitle.strip()

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

				if purpose == allowed_purpose[0]:
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
									'content': bodystring,
									'headerID': "1Rop1YKilizMmOSYt24D8M2LMwiM2oeb6"
							})

							for email in all_users:
								message = (settings.EMAIL_SUBJECT_PREFIX + new_ann.title, bodystring, html_design, email_from, [email] )
								email_mass.append(message)

							send_mass_html_mail( tuple(email_mass), fail_silently=False)

							if settings.DEBUG:
								print("Emails sent!")
								print(all_users)

					retjson["redirect_url"] = reverse('announcement_view', args=[str(new_ann.id)])
					
				elif purpose == allowed_purpose[1]:
					
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
			if purpose == allowed_purpose[0]:
				context['title'] = "Create Announcement"
			elif purpose == allowed_purpose[1]:
				edit_ann = Announcement.objects.filter(id=id).first()
				edit_ann_json = json.dumps(edit_ann.body)

				initialvalue = {}

				if edit_ann.imageID:
					initialvalue['imageID'] = edit_ann.imageID

				image_form = ImportImageForm(initial=initialvalue)

				context.update({
					'edit_ann': edit_ann, 
					'edit_ann_json': edit_ann_json,
					'image_form': image_form
				})
				context['title'] = "Edit Announcement"

			context["currpage"] = "announcements"
			return render(request, 'reviewer/admin/announcement/announcement.html', context)
	else:
		raise PermissionDenied()

@login_required
def admin_course_list(request):
	
	if request.user.is_superuser:
		courselist = Course.objects.order_by('code', 'number_len', 'number')
		currpage = "courses"
		context = {'courselist': courselist, 'currpage': currpage}

		return render(request, 'reviewer/admin/courses/course-list.html', context)
	else:
		raise PermissionDenied()

@login_required
def admin_course(request, course_id=""):
	return admin_get_course(request, "add", "", "")

@login_required
def admin_course_id(request, course_subj="", course_num ="", purpose="edit"):
	return admin_get_course(request, purpose, course_subj, course_num)

@login_required
def admin_get_course(request, purpose, course_subj="", course_num=""):

	purpose = purpose.lower()

	allowed_purpose = ['add', 'edit','delete', 'lessons', 'refs']
	if purpose not in allowed_purpose:
		raise Http404()

	referer = request.META.get('HTTP_REFERER', "")

	if request.user.is_superuser:
		if purpose == allowed_purpose[3]:
			return admin_course_lessons(request, course_subj, course_num)
		elif purpose == allowed_purpose[4]:
			return admin_course_ref(request, course_subj, course_num)
		elif purpose == allowed_purpose[2]:
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
					
				if purpose == allowed_purpose[0]:	
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
				elif purpose == allowed_purpose[1]:

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

			if purpose == allowed_purpose[0]:
				courseform = CourseForm()
				context = { 'courseform': courseform, 'courses': courselist, 'title': "Add Course" }

			elif purpose == allowed_purpose[1]:

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

			if request.method == "POST" and not request.user.check_password(request.POST['password']):
				context['error'] = "You entered the wrong password."

			if request.is_ajax():
				return render(request, 'reviewer/courses/course_add.html', context)
			else:	
				context["currpage"] = "courses"
				return render(request, 'reviewer/admin/courses/course_admin.html', context)
	
	else:
		raise PermissionDenied()

@login_required
def admin_course_lessons(request, course_subj="", course_num=""):

	if request.user.is_superuser:

		
		if request.method == 'GET':
			course = Course.objects.filter(code__iexact=course_subj).filter(number__iexact=str(course_num)).first()

			if course:
				lessons = Lesson.objects.filter(course=course).order_by('order')
				currpage = "courses"
				context = {'course': course, 'lessons': lessons, 'currpage': currpage}

				return render(request, 'reviewer/admin/courses/course-lessons.html', context)
			else:
				raise Http404()

		elif request.method == 'POST':

			data = request.POST
			order = data.getlist('order[]')
			lesson_bulk = Lesson.objects.filter(course__code__iexact=course_subj).filter(course__number__iexact=str(course_num)).order_by('order').in_bulk()
			error = None

			if len(order) == len(set(order)):
				if len(lesson_bulk) == len(order):
					for index, lsn in enumerate(lesson_bulk):
						lesson_bulk[lsn].order = order[index]
					Lesson.objects.bulk_update(lesson_bulk.values(), ['order'])
				else:
					error = "An operation has occured during this process. Please refresh the page."
			else:
				error = "Non-unique order values found. Exception handled."

			return JsonResponse({'error': error})

	else:
		raise PermissionDenied()

@login_required
def admin_course_ref(request, course_subj="", course_num=""):
	if request.user.is_superuser:
		coursefilter = Course.objects.filter(code__iexact=course_subj).filter(number__iexact=str(course_num)).first()

		if coursefilter:
			if request.is_ajax():
				error = "Failed to connect. Please refresh the page or try again later."
				result = None

				for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
					try:
						service = gdrive_connect()
						reffolder = 'references/{}'.format(coursefilter.name)
						reffolder = gdrive_traverse_path(service, path=reffolder, create=True)

						if request.method == "GET":
							result = {'obj': gdrive_list_meta_children(service, folderID=reffolder['id'], order="name")}
							result = render_to_string('reviewer/partials/course/course-refs-admin.html', { 'result': result['obj'] , 'course' : coursefilter }).strip()
						elif request.method == "POST":
							file_uploaded = request.FILES.get('file', None)

							if file_uploaded:
								file_uploaded = file_uploaded.open()
								file_bytes = BytesIO(file_uploaded.read())

								metadata = {'name': str(file_uploaded), 'parents': [reffolder['id']] }
								result = gdrive_upload_bytes_tofile(service, file_bytes, metadata, file_mime)
						elif request.method == "DELETE":
							gdrive_delete_file(service, request.body.decode('utf-8'))
						break
					except Exception as e:
						if settings.DEBUG: print(e)
				
				return JsonResponse({ 'result' : result })
			else:
				context = {
					'course' : coursefilter,
					'currpage' : 'courses'
				}

				return render(request, 'reviewer/admin/courses/course-reference.html', context)
		else:
			raise Http404()
	else:
		raise PermissionDenied()

@login_required
def admin_langlist(request):
	
	if request.user.is_superuser:
		langlist = Language.objects.order_by('name')
		currpage = "languages"
		
		context = {'langlist': langlist, 'currpage': currpage}
		return render(request, 'reviewer/admin/language/lang-list.html', context)
	else:
		raise PermissionDenied()

@login_required
def admin_lang_add(request):
	return admin_lang(request, "add", "")

@login_required
def admin_lang(request, purpose, id=""):

	purpose = purpose.lower()
	allowed_purpose = ['add', 'edit','delete']
	if purpose not in allowed_purpose:
		raise Http404()

	error = None
	if request.user.is_superuser:
		if purpose == allowed_purpose[2]:
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
					if purpose == allowed_purpose[0]:
						Language.objects.create(name=data['name'].strip(), color=data['color'][1:], imageID=image_uploadedID)
					elif purpose == allowed_purpose[1]:
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
				if purpose == allowed_purpose[0]:
					langform = LanguageForm(initial= {'color' : '868686'})

					context['langform'] = langform
					context['title'] = "Add Language"
				elif purpose == allowed_purpose[1]:
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

				if (request.method == "POST") and not request.user.check_password(request.POST['password']):
					context['error'] = "You entered the wrong password."

				context["currpage"] = "languages"
				return render(request, 'reviewer/admin/language/language.html', context)
	else:
		raise PermissionDenied()


@login_required
def admin_lessons_add(request):
	return admin_lessons_crud(request, 'add')

@login_required
def admin_lessons_crud(request, purpose, id=""):

	purpose = purpose.lower()
	allowed_purpose = ['add', 'edit','delete', 'question']
	if purpose not in allowed_purpose:
		raise Http404()

	if request.user.is_superuser:
		
		if purpose == allowed_purpose[3]:
			return admin_lessons_question_cud(request, id)
		elif request.method == 'POST':

			edit_lesson = Lesson.objects.filter(id=id).first() if (purpose == allowed_purpose[1]) or (purpose == allowed_purpose[2]) else None

			if purpose == allowed_purpose[2]:
				if edit_lesson:
					course = edit_lesson.course
					current_order = edit_lesson.order
					edit_lesson.delete()
					Lesson.objects.filter(order__gt=current_order).update(order=F('order')-1)

					return redirect('admin_course_id', course.code.lower(), course.number, 'lessons')
				else:
					raise Http404()
			else:
				data = request.POST

				lessonname = data.get('name', False).strip()
				course = data.get('course', False).strip()
				course = Course.objects.filter(pk=course).first()

				if (lessonname and course):
					
					verified = data.getlist('lesson_verified', False)
					verifier = data.get('verifiedby', '').strip() if verified else ''

					if purpose == allowed_purpose[0]:

						current_lessons = course.lesson_set.all()

						new_lesson = Lesson.objects.create(
							name = lessonname,
							course = course,
							extra = data.get('lesson_extra', False),
							lab_lesson = data.get('lesson_lab', False),
							verified = bool(verified),
							verifier = verifier,
							order = course.lesson_set.count() + 1
						)

						related_lessons = data.getlist('related')

						try:
							if len(related_lessons) > 0 and related_lessons[0] != '':
								new_lesson.rel_lesson.set(Lesson.objects.filter(id__in=related_lessons))
						except:
							pass

					elif edit_lesson:

						edit_lesson.name = lessonname
						edit_lesson.course = course
						edit_lesson.extra = data.get('lesson_extra', False)
						edit_lesson.lab_lesson = data.get('lesson_lab', False)
						edit_lesson.verified = bool(verified)
						edit_lesson.verifier = verifier

						edit_lesson.save()
					else:
						raise Http404()

					return redirect('admin_course_id', course.code.lower(), course.number, 'lessons')

				else:
					if purpose == allowed_purpose[0]:
						return redirect('admin_lessons_add')
					elif purpose == allowed_purpose[1]:
						return redirect('admin_lesson', edit_lesson.id)
		else:

			query = request.GET
			courses = Course.objects.all()
			lessons = Lesson.objects.all()
			edit_lesson = None
			select_course = query.get('course', False)
			select_course = courses.filter(id=select_course).first() if select_course else None

			currpage = "courses"
			context = {
				'courses': courses,
				'rel_lessons' : lessons,
				'currpage': currpage,
				'select_course' : select_course
			}

			if purpose == allowed_purpose[0]:
				context['title'] = "Add Lesson"
			elif purpose == allowed_purpose[1]:
				context['edit_lesson'] = lessons.filter(id=id).first()
				context['rel_lessons'] = lessons.exclude(id=id)
				context['title'] = "Edit Lesson"

			return render(request, 'reviewer/admin/courses/lessons/lessons.html', context)
	else:
		raise PermissionDenied()

@login_required
def admin_lessons_question_cud(request, id=""):

	if request.user.is_superuser:

		lesson = Lesson.objects.filter(id=id).first()
		
		if lesson:
			if request.method == 'POST':

				data = 	request.POST
				qtype = data.get('qtype', None)
				error = None
				question = None
				language = None

				existingq = lesson.question_set.first()

				if existingq:
					if existingq.qtype == "code" and qtype == "code":
						otherq = lesson.question_set.filter(qtype='code').values_list('lang', flat=True)
						language = Language.objects.exclude(id__in=otherq).first()

						error = otherq
					else:
						error = "You may only add multiple coding questions or one non-coding question."

				else:
					question = Question.objects.create(
						lesson = lesson,
						lang =language,
						qtype=qtype
					)

					question_html = render_to_string('reviewer/admin/courses/lessons/questions/questions_partial.html', {'question': question, 'user': request.user }).strip()

				if request.is_ajax():
					return JsonResponse({'question': question_html if question else question, 'error': error})
				else:
					return redirect('admin_lesson', id, 'edit')
			else:
				edit_lesson_codes = lesson.question_set.filter(qtype='code').values_list('lang', flat=True)

				currpage = "courses"
				context = {
					'edit_lesson': lesson,
					'codeq' : edit_lesson_codes,
					'currpage': currpage,
					'title': "Add Question"
				}

				return render(request, 'reviewer/admin/courses/lessons/questions/questions{}.html'.format('_add' if request.is_ajax() else ''), context)
		else:
			raise Http404('Lesson not found.')
	else:
		raise PermissionDenied()

@login_required
def admin_lessons_question(request, purpose, id="", qid=""):

	if request.user.is_superuser:

		purpose = purpose.lower()
		question = Question.objects.filter(lesson__id=id, id=qid).first()
		allowed_purpose = ['module', 'build', 'delete']

		if question and purpose in allowed_purpose:
			if request.method == 'POST':
				if purpose == allowed_purpose[0]:
					return None
				elif purpose == allowed_purpose[1]:
					question.custom_code = request.POST.dict()
					question.save(update_fields=['custom_code'])
					return JsonResponse({'redirect_url': reverse('admin_lesson', args=[str(id), 'edit']) })
			elif request.method == 'GET':
				context = {'question': question}
				if purpose == allowed_purpose[0]:
					pass
				elif purpose == allowed_purpose[1]:
					if question.custom_code:
						context['import_qcode'] = question.custom_code['code']
					else: 
						context['import_qcode'] = "function question(){\n\n}"
					return render(request, 'reviewer/admin/courses/lessons/questions/questions_build.html', context)
				elif purpose == allowed_purpose[2]:
					question.delete()
					return redirect('admin_lesson', id, 'edit')
		else:
			raise Http404()
	else:
		raise PermissionDenied()

@login_required
def admin_users(request):

	current_page = "users"
	
	if request.user.is_superuser:
		users = ImportUser.objects.order_by('username')
		context = {}

		if (request.method == "POST"):

			data = request.POST
			confirm = authenticate(username=request.user.username, password=data["password"])
	
			if confirm == request.user:
				find_uname = ImportUser.objects.filter(username=data["username"]).first()
				find_uname.is_superuser = not find_uname.is_superuser
				find_uname.save()
				context ['message'] = "You have changed {}'s superuser status.".format(data["username"])
			else:
				context ['message'] = "You entered the wrong password."

		context.update({ 'users' : users, 'currpage' : current_page })

		return render(request, 'reviewer/admin/users.html', context)

	else:
		raise PermissionDenied()


