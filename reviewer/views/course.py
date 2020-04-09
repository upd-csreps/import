
from ..models import Course, Comment, Likes, Announcement
from ..forms import CourseForm, CommentForm
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.html import escape
from django.urls import reverse
from math import ceil
from PIL import Image
import re

hlink_regex = "(?:^|\b|\s)((?:([A-Za-z][A-Za-z0-9+.-]*):)?(?:\/\/)?(?:([-A-Za-z0-9_'](?:(?:\.?(?:[-A-Za-z0-9_'~]|%[A-Fa-f]{2}))*[-A-Za-z0-9_'])?)(?::((?:[-A-Za-z0-9_'~!$&()\*+,;=]|%[A-Fa-f]{2})*))@)?((?:localhost)|(?:(?:1?[0-9]{1,2}|2[0-5]{1,2})(?:\.(?:1?[0-9]{1,2}|2[0-5]{1,2})){3})|(?:\[(?:[0-9A-Fa-f:]+:[0-9A-Fa-f:]+)+\])|(?:(?:[Ww]{3}\.)?[A-Za-z0-9](?:(?:\.?[-A-Za-z0-9])*[A-Za-z0-9])?\.[A-Za-z0-9](?:[-A-Za-z0-9]*[A-Za-z0-9])?))(?::[0-9]+)?((?:\/(?:[-A-Za-z0-9._~:@!$&'()*+,;=]|%[A-Fa-f]{2})+)*\/?)(\?(?:[-A-Za-z0-9._~:@!$&'()*+,;=/?]|%[A-Fa-f]{2})*)?(#(?:[-A-Za-z0-9._~:@!$&'()*+,;=/?]|%[A-Fa-f]{2})*)?)(?:\b|\s|$)"

def hlinkify(string, url_trunct):

	comment_body = string
	hlinkdata = re.findall( hlink_regex, comment_body)

	for link in hlinkdata:
		urltrunc = escape(link[0][0:url_trunct]+'...')
		if not (link [4] == 'youtube.com' and link[4] == 'youtu.be' ):
			comment_body = comment_body.replace(link[0], '<a class="d-inline-flex import-ex-link" target="_blank" href="{}{}">{}</a>'.format("" if link[1] else "http://",link[0], urltrunc if len(link[0]) > url_trunct else escape(link[0]) ))
		else:
			comment_body = comment_body.replace(link[0], '<a class="d-inline-flex import-ex-link" target="_blank" href="{}{}">{}</a>'.format("" if link[1] else "http://",link[0], urltrunc if len(link[0]) > url_trunct else escape(link[0]) ))

	return comment_body


def comment_delete(request, course, startindex, pagect_limit):

	data = request.body
	comment_findid = data.decode('utf-8').split("-")[1]

	delcom = Comment.objects.filter(pk=comment_findid).first()
	result = {}
	if (request.user == delcom.user_attr):
		delcom.delete()

		all_course_comments = Comment.objects.filter(course_attr=course).order_by('-date_posted')
		course_comment_count = len(all_course_comments)
		page_ct = int(ceil(course_comment_count/pagect_limit))
		comment_html = None

		try:
			last_comment = all_course_comments[startindex+pagect_limit-1]
			last_comment_likestat = last_comment.likes_set.filter(user_attr=request.user).first()
			last_comment = {
				'base' : last_comment,
				'proc' : hlinkify(new_comment.body, 33),
				'liked' : bool(last_comment_likestat)
			}

			comment_html = render_to_string('reviewer/partials/comment.html', { 'comment': last_comment, 'request': request, 'user' : request.user }).strip()

		except IndexError as e:
			if settings.DEBUG:
				print(e)

		result.update({
			'comment_html' : comment_html,
			'course_comment_count' : course_comment_count,
			'page_count' : page_ct
		})

		if len(all_course_comments) == 0:
			result['empty_html'] = render_to_string('reviewer/partials/course/course-comment-empty.html', { 'request': request, 'user' : request.user }).strip()

	return JsonResponse(result)

def comment_add(request, pass_args):

	data = request.POST
	resultid = None 

	response = redirect( reverse('course', args=[pass_args['csubj'], str(pass_args['cnum'])]) + 'c/1/' )

	cpagect = pass_args['commentpage']['count']
	npagect = int(ceil( (pass_args['course_commentstotal']+1) / pass_args['commentpage']['limit'] ))

	if request.user.is_authenticated:
		image_uploaded = request.FILES.get('image', None)

		try:
			image_test =  Image.open(image_uploaded)
			image_test.verify()
			
		except:
			image_uploaded = None

		new_comment = Comment.objects.create(course_attr=pass_args['course_filt'], user_attr=request.user, body=data['body'], image=image_uploaded)	
		resultid = new_comment.id

		## Replace HTML content here

		new_comment = {
			'base' : new_comment,
			'proc' : hlinkify(new_comment.body, 33),
			'liked' : False
		}

		comment_html = render_to_string('reviewer/partials/comment.html', { 'comment': new_comment, 'request': request, 'user' : request.user }).strip()
		if pass_args['commentpage']['current'] == 1:

			data = { 
				'commentid': resultid,
				'comment_html' : comment_html
			}

			if (npagect != cpagect) and ((pass_args['course_commentstotal']+1) > pass_args['commentpage']['limit']):
				pass_args['commentpage']['count'] = npagect
				pass_args.update({ 'request': request, 'user' : request.user })
				data['page_create'] = render_to_string('reviewer/partials/course/course-comments-pagination.html', pass_args ).strip()
			else:
				data['page_create'] = ''
			
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
				liked_comment = render_to_string('reviewer/partials/comment.html', { 'comment': liked_comment, 'request': request, 'user' : request.user }).strip()
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

	coursefilter = Course.objects.filter(code__iexact=csubj).filter(number__iexact=str(cnum)).first()

	if coursefilter:

		cpage = 1 if int(cpage) < 1 else int(cpage)
		pagect_limit = settings.IMPORT_COMMENT_CT	

		startindex = pagect_limit*(cpage - 1)
		all_course_comments = coursefilter.comment_set.order_by('-date_posted')
		course_comments_filtered = all_course_comments[startindex:startindex+pagect_limit]
		course_commentstotal = len(all_course_comments)

		page_ct = int(ceil(course_commentstotal/pagect_limit))

		commentpage = {
				'current': cpage,
				'prev' : cpage-1,
				'next'	: cpage+1,
				'count': page_ct,
				'limit' : pagect_limit
		}

		if commentpage['current'] > commentpage['count'] and commentpage['count'] != 0:
			return redirect('course', csubj, cnum)
		else:
			if request.method == "POST":
				pass_args = { 	'course_filt': coursefilter,
								'csubj': csubj,
								'cnum' : cnum,
								'course_commentstotal' : course_commentstotal,
								'commentpage' : commentpage
							}
				return comment_add(request, pass_args)
			elif request.method == "DELETE":
				return comment_delete(request, coursefilter, startindex, commentpage['limit'])
			elif request.method == "GET":

				liked_comments = list(Likes.objects.filter(user_attr=request.user).values_list('comment__id', flat=True)) if request.user.is_authenticated else [] 
				commentform = CommentForm(auto_id="comment-form", request=request)
				course_comments = { 'content' : [], 'form' : commentform, 'count' : course_commentstotal }

				for comment in course_comments_filtered:
					comment_body = hlinkify(comment.body, 33)
					
					# Add found links tab

					comment_index = {
						'base' : comment,
						'proc' : comment_body,
						'liked' : comment.id in liked_comments
					}

					course_comments['content'].append(comment_index)

				context = {
					'course_filt': coursefilter,
					'course_comments': course_comments,
					'section': catchar,
					'commentpage' : commentpage
				}

				return render(request, 'reviewer/courses/course.html', context)
	else:
		raise Http404("Course not found.")
