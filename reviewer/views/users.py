import os
import json

from ..models import ImportUser, Comment, Likes, Language, Announcement
from ..forms import ImportUserCreationForm, CommentForm

from django.conf import settings
from django.contrib.auth import authenticate, login,logout

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

from django.urls import reverse

from PIL import Image


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
