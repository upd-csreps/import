
from ..models import Course, Comment, Likes, Announcement
from ..forms import CourseForm, CommentForm

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from math import ceil
from PIL import Image



def comment_delete(request, course, startindex, page_ct_limit):

	data = request.body
	comment_findid = data.decode('utf-8').split("-")[1]

	delcom = Comment.objects.filter(pk=comment_findid).first()
	result = {}
	if (request.user == delcom.user_attr):
		delcom.delete()

		all_course_comments = course.comment_set.order_by('-date_posted')
		course_comment_count = len(all_course_comments)
		page_ct = int(ceil(course_comment_count/page_ct_limit))
		try:
			last_comment = all_course_comments[startindex+page_ct_limit-1]
			result['comment_html'] = render_to_string('reviewer/partials/comment.html', { 'comment': last_comment, 'request': request, 'user' : request.user })

			last_comment_likestat = last_comment.likes_set.filter(user_attr=request.user)
			result['comment_likestate'] = { 
				'ID': last_comment_likestat.comment_id,
				'status': True if len(last_comment_likestat) != 0 else False
			}

		except IndexError:
			result.update({
				'comment_html' : None,
				'course_comment_count' : course_comment_count,
				'page_count' : page_ct
			})
			if len(all_course_comments) == 0:
				result['empty_html'] = render_to_string('reviewer/partials/course/course-comment-empty.html', { 'request': request, 'user' : request.user })

	return JsonResponse(result)

def comment_add(request, csubj, cnum, course):

	data = request.POST
	resultid = None 

	response = redirect( reverse('course', args=[csubj, str(cnum)]) + 'c/1/' )

	if request.user.is_authenticated:
		image_uploaded = request.FILES.get('image', None)

		try:
			image_test =  Image.open(image_uploaded)
			image_test.verify()
			
		except:
			image_uploaded = None

		new_comment = Comment.objects.create(course_attr=coursefilter[0], user_attr=request.user, body=data['body'], image=image_uploaded)	
		resultid = new_comment.id
		comment_html = render_to_string('reviewer/partials/comment.html', { 'comment': new_comment, 'request': request, 'user' : request.user })

		if cpage == 1:
			data = { 
				'commentid': resultid,
				'comment_html' : comment_html
			}
			
			response = JsonResponse(data)

	return response


def comment_like(request, csubj, cnum):

	if request.method == "POST":

		data = request.POST
		resultid = None

		if request.user.is_authenticated:

			comment_findid = data.get('commentID').split("-")[1]
			comm_all_like = Likes.objects.filter(comment_id=comment_findid).select_related('user_attr').select_related('comment').all()
			like_state = comm_all_like.filter(user_attr=request.user)
			liked_comment = Comment.objects.filter(id=comment_findid).first()

			if like_state:
				like_state.delete()
				like_state = False
				liked_comment  = None
			else:
				Likes.objects.create(comment_id=int(comment_findid), user_attr=request.user)
				liked_comment = render_to_string('reviewer/partials/comment.html', { 'comment': liked_comment, 'request': request, 'user' : request.user })
				like_state = True

			like_count_callback = {
				'count': len(comm_all_like), 
				'state': like_state,
				'com_html' : liked_comment
			}

			return JsonResponse(like_count_callback)
		else:
			raise PermissionDenied()


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
		all_course_comments = coursefilter[0].comment_set.order_by('-date_posted')
		course_comments_filtered = all_course_comments[startindex:startindex+page_ct_limit]
		course_commentstotal = len(all_course_comments)

		page_ct = int(ceil(course_commentstotal/page_ct_limit))

		if cpage > page_ct and page_ct != 0:
			return redirect('course', csubj, cnum)
		else:
			if request.method == "POST":
				return comment_add(request, csubj, cnum, coursefilter[0])
			elif request.method == "DELETE":
				return comment_delete(request, coursefilter[0], startindex, page_ct_limit)
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
					'next_page' : cpage+1,
					'page_limit' : page_ct_limit
				}

				return render(request, 'reviewer/courses/course.html', context)
	else:
		raise Http404("Course not found.")
