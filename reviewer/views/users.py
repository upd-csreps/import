
from ..models import ImportUser, Comment, Likes, Language
from ..forms import ImportUserCreationForm

from ..custom import *

from django.conf import settings
from django.contrib.auth import authenticate, login,logout

from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render

from django.urls import reverse
from io import BytesIO
from PIL import Image

# User Views

def user_get(request, user_filter, error=None):

	thousand_counter = [10**9, 10**6, 10**3]
	thousand_marker = ['B', 'M', 'K']
	liked_comments = []
	liked_comments_data = []

	if (len(user_filter) > 0):

		comments = user_filter[0].comment_set.order_by('-date_posted')

		if request.user.is_authenticated:
			liked_comments = list(Likes.objects.filter(user_attr=request.user).values_list('comment__id', flat=True))

		target_user_likes = Likes.objects.filter(user_attr=user_filter[0]).select_related('comment').all().reverse()

		for like in target_user_likes:
			liked_comments_data.append(like.comment)
	
		user_comments_count, liked_comments_data_count = len(comments), len(liked_comments_data)

		for index, item in enumerate(thousand_counter):
			if isinstance(user_comments_count, int) and user_comments_count >= item:
				user_comments_count = (user_comments_count//item) + thousand_marker[index]
			if isinstance(liked_comments_data_count, int) and liked_comments_data_count >= item:
				liked_comments_data_count = (liked_comments_data_count//item) + thousand_marker[index]
			
		
		context = {
			'user_filt': user_filter[0],
			'user_comments':comments , 
			'error': error,
			'liked_comments': liked_comments,
			'liked_comments_data' : liked_comments_data,
			'comments_count' : user_comments_count,
			'liked_comments_data_count' : liked_comments_data_count
		}
		return render(request, 'reviewer/user/user.html', context)
	else:
		raise Http404("User does not exist.")

def user(request, username):

	user_filter = ImportUser.objects.filter(username=username)
	error = None

	if request.method == 'POST':
		if user_filter[0].username == request.user.username:
			utest = ImportUser.objects.filter(username=username).first()

			image_uploaded = request.FILES.get('image', None)

			try:
				image_test =  Image.open(image_uploaded)
				image_test.verify()

				image_test =  Image.open(image_uploaded)
				image_test.thumbnail((800,800))
				image_bytes = BytesIO()
				image_test.convert('RGB').save(image_bytes, format='JPEG')	### 

				for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
					try:
						service = gdrive_connect()
						userfolder = 'media/users/{}'.format(utest.username)
						userfolder = gdrive_traverse_path(service, path=userfolder, create=True)

						metadata = {'name': 'profile_pic.jpg', 'parents': [userfolder['id']] }
						oldprofpicID = utest.prof_picID
						utest.prof_picID = gdrive_upload_bytes_tofile(service, image_bytes, metadata, 'image/jpeg')
						break
					except Exception as e:
						if settings.DEBUG: print(e)

				if oldprofpicID != None: gdrive_delete_file(service, oldprofpicID)
				utest.save(update_fields=['prof_picID'])	
			except Exception as e:
				if settings.DEBUG: print(e)
				error = "Upload failed. Try uploading again in a few moments." if isinstance(e, TimeoutError) else "Upload a valid image file or try again."

		if request.is_ajax():

			response = {'error' : error}

			return JsonResponse(response);
		else:
			return user_get(request, user_filter, error)
	else:
		return user_get(request, user_filter)
		
def user_settings_uname_is_unique(request, uname):
	return True if ( (not ImportUser.objects.filter(username=uname).exists()) or uname == request.user.username) else False

def user_settings(request):

	willRender = True
	error = []

	if request.user.is_authenticated:
		if request.method == 'POST':

			queries, data = request.GET, request.POST
			
			if (queries.get("unamecheck") == 'y'):

				unamecheck_callback = { 'valid': 'n' }

				if not data["uname"]:
					unamecheck_callback['valid'] = 'e'
				elif (data["uname"] == request.user.username):
					unamecheck_callback['valid'] = 's'
				elif (user_settings_uname_is_unique(request, data["uname"])):
					unamecheck_callback['valid'] = 'y'
					
				return JsonResponse(unamecheck_callback)

			elif (queries.get("delete") == 'true'):

				userauth = authenticate(username=request.user.username, password=data.get("password"))
				willRender = False

				if userauth == request.user:

					logout(request)
					userauth.delete()

					## Delete GDrive Data ##

					for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
						try:
							service = gdrive_connect()
							userfolder = 'media/users/{}'.format(request.user.username)
							userfolder = gdrive_traverse_path(service, path=userfolder, create=True)
							gdrive_delete_file(service, userfolder['id'])
							break
						except Exception as e:
							if settings.DEBUG:
								print(e)

					return redirect('index')
				else:
					return redirect('user_settings')
			else:

				emptyreqfields = []

				if not data["username"]:
					emptyreqfields.append("username")
				if not data["first_name"]:
					emptyreqfields.append("first_name")
				if not data["last_name"]:
					emptyreqfields.append("last_name")
				if not data["e-mail"]:
					emptyreqfields.append("e-mail")
				if not data["course"]:
					emptyreqfields.append("course")

				if len(emptyreqfields) == 0:

					currentuname = request.user.username
					currentuser = request.user

					username_valid = user_settings_uname_is_unique(request, data["username"])

					if (username_valid):

						currentuser.username = data["username"]
						currentuser.first_name = data["first_name"]
						currentuser.middle_name = None if not data["middle_name"] else data["middle_name"]
						currentuser.last_name = data["last_name"]
						currentuser.suffix = data["suffix"]
						currentuser.studentnum = None if not data["studentnum"] else data["studentnum"]
						currentuser.show_studentnum = (data.get("show_studentnum") == 'show')
						currentuser.email = data["e-mail"]
						currentuser.show_email = (data.get("show_email") == 'show')
						currentuser.course = data["course"]
						currentuser.fave_lang = Language.objects.filter(name=data["fave_lang"]).first() if data.get("fave_lang", None) else None
						currentuser.dark_mode = (data.get("dark_mode") == 'dark')
						currentuser.notifications = (data.get("em_notif") == 'notif_on')

						if currentuname != data["username"] and currentuser.prof_picID:
							for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
								try:
									service = gdrive_connect()
									userfolder = 'media/users/{}'.format(currentuname)
									userfolder = gdrive_traverse_path(service, path=userfolder, create=True)
									newfolder = gdrive_update_file(service, userfolder['id'], file_metadata={"name": data["username"]})

									if newfolder != False:
										if newfolder.get("name", None) == data["username"]:
											break
								except Exception as e:
									if settings.DEBUG: print(e)
							
						currentuser.save(force_update=True)

						willRender = False

						return redirect('user', request.user.username)
				else:
					error = emptyreqfields

		if willRender:

			langlist = Language.objects.all()

			userpassword = request.user.password.split("$")

			userpassword[2] = userpassword[2][0:6] + ('*' * (len(userpassword[2])-6) )
			userpassword[3] = userpassword[3][0:6] + ('*' * (len(userpassword[3])-6) )

			hasEmptyFields = False

			if not (request.user.username and request.user.first_name and request.user.last_name and request.user.email):
				hasEmptyFields = True

			context = {'userpassword_algo' : userpassword[0], 
						'userpassword_iterations': userpassword[1],
						'userpassword_salt' : userpassword[2], 
						'userpassword_hash' : userpassword[3],
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

		if (currURL != settings_url) and not (usr.username and usr.first_name and usr.last_name and usr.email):
			willRedirect = True

		data = {'field_redirect': willRedirect, 'url_redirect': settings_url }

		return JsonResponse(data)
	else:
		raise Http404()


def register(request):

	langlist = Language.objects.all()

	if request.method == 'POST':
		
		queries, data = request.GET, request.POST
		
		if (queries.get("unamecheck") == 'y'):

			unamecheck_callback = {
				'valid': 'n'
			}

			if (data["uname"] == ""):
				unamecheck_callback['valid'] = 'e'
			elif (data["uname"] == request.user.username):
					unamecheck_callback['valid'] = 's'
			elif (user_settings_uname_is_unique(request, data["uname"].strip())):
				unamecheck_callback['valid'] = 'y'

			return JsonResponse(unamecheck_callback)

		else:

			form = ImportUserCreationForm(request.POST)
			username = form.cleaned_data['username'].strip()
			if form.is_valid() and user_settings_uname_is_unique(request, username):
				
				password = form.cleaned_data['password1']
				user = authenticate(username=username, password=password)
				form.save()

				login(request, user)
				return redirect('user_settings')

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
