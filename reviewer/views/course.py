
from ..models import Course, Comment, Likes, Announcement
from ..forms import CourseForm, CommentForm

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from math import ceil
from PIL import Image


def courselist(request):

	courselist = Course.objects.filter(visible=True).order_by('code', 'number_len', 'number')
	announcements = Announcement.objects.order_by('-datepost')[0:5]

	context = {'courselist': courselist, 'announcements': announcements  }
	return render(request, 'reviewer/courses/course-list.html', context)

def course(request, csubj, cnum):
	return coursecpage( request, csubj, cnum, 'l', '1')

def coursecpage(request, csubj, cnum, catchar = 'l', cpage = 1):

	if not catchar:
		catchar = "l"
		cpage = 1

	if not cpage: cpage = 1
	cpage = int(cpage)
	page_ct_limit = settings.IMPORT_COMMENT_CT	

	coursefilter = Course.objects.filter(code__iexact=csubj).filter(number__iexact=str(cnum))

	if (len(coursefilter) > 0):
		if cpage < 1: cpage = 1

		startindex = (cpage - 1)*page_ct_limit
		all_courses = coursefilter[0].comment_set.order_by('-date_posted')
		course_comments_filtered = all_courses[startindex:startindex+page_ct_limit]
		course_commentstotal = len(all_courses)

		page_ct = int(ceil(course_commentstotal/page_ct_limit))

		if cpage > page_ct and page_ct != 0:
			return redirect('course', csubj, cnum)
		else:
			if request.method == "POST":

				data = request.POST
				resultid = None 

				response = redirect( reverse('coursecpage', args=[csubj, str(cnum), 'c', '1']) )

				if request.user.is_authenticated:
					image_uploaded = request.FILES.get('image', None)

					try:
						image_test =  Image.open(image_uploaded)
						image_test.verify()
						
					except:
						image_uploaded = None

					# Add input validation
					Comment.objects.create(course_attr=coursefilter[0], user_attr=request.user, body=data['body'], image=image_uploaded)	
					resultid = new_comment.id

					if cpage == 1:
						data = {'commentid': resultid }
						if new_comment.image:
							data['image'] =  new_comment.image.url
						response = JsonResponse(data)

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
								'user_url': str(reverse('user', args=[str(last_comment.user_attr.username)])),
								'body' : str(last_comment.body),
								'date' : str(last_comment.date_posted),
								'liked' : likedstat,
								'like_ct' : last_comment.likes_set.all().count()
							 }

							if last_comment.image:
								result["image"]	= str(last_comment.image.url)
							if last_comment.user_attr.prof_pic:
								result['user_img'] = str(last_comment.user_attr.prof_pic.url),
					except IndexError:
						pass

				return JsonResponse(result)

			elif request.method == "GET":

				liked_comments = None
				commentform = CommentForm(auto_id="comment-form", request=request)

				if request.user.is_authenticated:
					liked_comments = list(Likes.objects.filter(user_attr=request.user).values_list('comment__id', flat=True))

				context = {
						'course_filt': coursefilter[0],
						'course_comment_count': course_commentstotal,
						'course_comments': course_comments_filtered,
						'comment_form': commentform,
						'liked_comments': liked_comments,
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

		if request.user.is_authenticated:

			comment_findid = data.get('commentID').split("-")[1]
			comm_all_like = Comment.objects.filter(pk=comment_findid).first().likes_set.all()
			like_state = comm_all_like.filter(user_attr=request.user)

			if like_state:
				like_state.delete()
				like_state = False
			else:
				Likes.objects.create(comment_id=int(comment_findid), user_attr=request.user)
				like_state = True

			like_count_callback = {
				'count': len(comm_all_like), 
				'state': like_state
			}

			return JsonResponse(like_count_callback)
		else:
			raise PermissionDenied()

