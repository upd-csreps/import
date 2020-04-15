
from ..custom import *
from ..models import Course, Comment, Likes, Announcement
from ..forms import CourseForm, CommentForm

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.html import escape
from django.urls import resolve

from io import BytesIO
from math import ceil
from PIL import Image
from urllib.parse import parse_qs
import re
import mimetypes

hlink_regex = "(?:^|\b|\s)((?:([A-Za-z][A-Za-z0-9+.-]*):)?(?:\/\/)?(?:([-A-Za-z0-9_'](?:(?:\.?(?:[-A-Za-z0-9_'~]|%[A-Fa-f]{2}))*[-A-Za-z0-9_'])?)(?::((?:[-A-Za-z0-9_'~!$&()\*+,;=]|%[A-Fa-f]{2})*))@)?((?:localhost)|(?:(?:1?[0-9]{1,2}|2[0-5]{1,2})(?:\.(?:1?[0-9]{1,2}|2[0-5]{1,2})){3})|(?:\[(?:[0-9A-Fa-f:]+:[0-9A-Fa-f:]+)+\])|(?:[A-Za-z0-9](?:(?:\.?[-A-Za-z0-9])*[A-Za-z0-9])?\.[A-Za-z0-9](?:[-A-Za-z0-9]*[A-Za-z0-9])?))(?::[0-9]+)?((?:\/(?:[-A-Za-z0-9._~:@!$&'()*+,;=]|%[A-Fa-f]{2})+)*\/?)(\?(?:[-A-Za-z0-9._~:@!$&'()*+,;=/?]|%[A-Fa-f]{2})*)?(#(?:[-A-Za-z0-9._~:@!$&'()*+,;=/?]|%[A-Fa-f]{2})*)?)(?:\b|\s|$)"

def hlinkify(string, url_trunct):

	comment_body = string
	hlinkdata = re.findall( hlink_regex, comment_body)
	media = ''

	for link in hlinkdata:
		
		urltrunc = escape(link[0][0:url_trunct]+'...')
		embeds_dir = 'reviewer/partials/media-embeds'

		if not media:
			if (link [4] == 'www.youtube.com'  or link[4] == 'youtube.com' or link[4] == 'youtu.be' ):
				if link[4] == 'youtu.be' and link[5]:
					yt_id = link[5][1:]
				elif link[6]:
					yt_id = parse_qs(link[6][1:])['v']
				media = render_to_string(embeds_dir + '/youtube-embed.html', { 'youtubeID': yt_id }).strip()
			elif (link [4] == 'facebook.com' or link[4] == 'www.facebook.com'):
				fb_type = ''
				if 'video' in link[5]:
					fb_type = 'video'
				elif 'comment' in link[6]:
					fb_type = 'comment'
				elif 'post' in link[5]:
					fb_type = 'post'

				if fb_type:
					media = render_to_string(embeds_dir + '/fb-embed.html', { 'type': fb_type, 'fb_link': 'http://{}{}{}'.format(link[4],link[5],link[6]) }).strip()
				else:
					pass
			elif (link [4] == 'twitter.com' or link [4] == 'www.twitter.com'):
				media = render_to_string(embeds_dir + '/tweet-widget.html', { 'twitter_link': 'http://{}{}'.format(link[4],link[5]) }).strip()
			elif (link [4] == 'giphy.com'):
				giphy_ID = link[5].split('-')
				giphy_ID = giphy_ID[len(giphy_ID)-1]
				media = render_to_string(embeds_dir + '/giphy-embed.html', { 'giphy_ID': giphy_ID, 'giphy_link': link[0] }).strip()
			elif (link [4] == 'www.desmos.com'):
				media = render_to_string(embeds_dir + '/desmos-embed.html', { 'desmos_link': link[0] }).strip()
			elif (link [4] == 'codepen.io'):
				pen_paths  = link[5][1:].split('/')
				media = render_to_string(embeds_dir + '/codepen-embed.html', { 'pen_user': pen_paths[0], 'pen_slug': spotify_paths[2], 'user' : request.user  }).strip()
			elif (link [4] == 'open.spotify.com' and link[5]):
				spotify_paths = link[5][1:].split('/')
				media = render_to_string(embeds_dir + 'spotify-widget.html', { 'spotify_embed': spotify_paths[0], 'spotify_id': spotify_paths[1], 'user' : request.user }).strip()
			elif (link [4] == 'github.com'):
				media = render_to_string(embeds_dir + '/github-button.html', { 'github_link': link[0] }).strip()

		comment_body = comment_body.replace(link[0], '<a class="d-inline-flex import-ex-link" target="_blank" href="{}{}">{}</a>'.format("" if link[1] else "http://",link[0], urltrunc if len(link[0]) > url_trunct else escape(link[0]) ))

	return { 'body' : comment_body, 'media' : media}

def comment_delete(request, course, startindex, pagect_limit):

	data = request.body
	comment_findid = data.decode('utf-8').split("-")[1]

	delcom = Comment.objects.filter(pk=comment_findid).first()
	result = {}
	if (request.user == delcom.user_attr):

		if delcom.imageID:
			for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
				try:
					service = gdrive_connect()
					gdrive_delete_file(service, delcom.imageID)
					break
				except Exception as e:
					if settings.DEBUG: print(e)

		delcom.delete()

		all_course_comments = Comment.objects.filter(course_attr=course).order_by('-date_posted')
		course_comment_count = len(all_course_comments)
		page_ct = int(ceil(course_comment_count/pagect_limit))
		comment_html = None


		try:
			if resolve(request.path)[0] != 'user':
				last_comment = all_course_comments[startindex+pagect_limit-1]
				last_comment_likestat = last_comment.likes_set.filter(user_attr=request.user).first()

				comment_finding = hlinkify(last_comment.body, 50)

				last_comment = {
					'base' : last_comment,
					'proc' : comment_finding['body'],
					'media' : comment_finding['media'],
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

	response = redirect('coursecpage', pass_args['csubj'], pass_args['cnum'], 'c', 1 )

	cpagect = pass_args['commentpage']['count']
	npagect = int(ceil( (pass_args['course_commentstotal']+1) / pass_args['commentpage']['limit'] ))

	if request.user.is_authenticated:
		image_uploaded = request.FILES.get('image', None)

		new_comment = Comment(course_attr=pass_args['course_filt'], user_attr=request.user, body=data['body'].strip(), imageID=image_uploaded)
		new_comment.save()

		try:
			image_test =  Image.open(image_uploaded)
			image_test.verify()

			image_test =  Image.open(image_uploaded)
			image_mime = mimetypes.guess_type(str(image_uploaded))[0]
			image_test.thumbnail((800,800))
			image_bytes = BytesIO()
			image_test.save(image_bytes, format=image_test.format)	### 

			for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
				try:
					service = gdrive_connect()
					userfolder = 'media/users/{}/comments'.format(request.user.username)
					userfolder = gdrive_traverse_path(service, path=userfolder, create=True)

					metadata = {'name': 'comment-{}.{}'.format(str(new_comment.id), image_test.format.lower()), 'parents': [userfolder['id']] }
					new_comment.imageID = gdrive_upload_bytes_tofile(service, image_bytes, metadata, image_mime)
					new_comment.save()
					break
				except Exception as e:
					if settings.DEBUG: print(e)

		except Exception as e:
			if settings.DEBUG: print(e)
			error = "Upload failed. Try uploading again in a few moments." if isinstance(e, TimeoutError) else "Upload a valid image file or try again."

		
		
		resultid = new_comment.id

		comment_finding = hlinkify(new_comment.body, 50)

		new_comment = {
			'base' : new_comment,
			'proc' : comment_finding['body'],
			'media' : comment_finding['media'],
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
				like_state = True

				if resolve(request.path)[0] == 'user':
					comment_finding = hlinkify(liked_comment.body, 50)
					liked_comment = {
						'base' : liked_comment,
						'proc' : comment_finding['body'],
						'media' : comment_finding['media'],
						'liked' : True
					}

					liked_comment = render_to_string('reviewer/partials/comment.html', { 'comment': liked_comment, 'request': request, 'user' : request.user }).strip()
				else:
					liked_comment = None


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
		course_commentstotal = len(all_course_comments)

		if ( ((course_commentstotal-1) < startindex) and (course_commentstotal != 0)):
			return redirect( 'coursecpage', csubj, cnum, 'c',  1 )
		else:
			
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

					course_comments_filtered = all_course_comments[startindex:startindex+pagect_limit]

					liked_comments = list(Likes.objects.filter(user_attr=request.user).values_list('comment__id', flat=True)) if request.user.is_authenticated else [] 
					commentform = CommentForm(auto_id="comment-form", request=request)
					course_comments = { 'content' : [], 'form' : commentform, 'count' : course_commentstotal }

					for comment in course_comments_filtered:
						comment_finding = hlinkify(comment.body, 50)

						comment_index = {
							'base' : comment,
							'proc' : comment_finding['body'],
							'media' : comment_finding['media'],
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



def course_ref(request, csubj, cnum):

	coursefilter = Course.objects.filter(code__iexact=csubj).filter(number__iexact=str(cnum)).first()
	retjson = {'error': "Failed to connect. Please refresh the page or try again later."}

	for i in range(1, settings.GOOGLE_API_RECONNECT_TRIES):
		try:
			service = gdrive_connect()
			reffolder = 'references/{}'.format(coursefilter.name)
			reffolder = gdrive_traverse_path(service, path=reffolder, create=True)

			retjson = {'obj': gdrive_list_meta_children(service, folderID=reffolder['id'], order="name")}
			break
		except Exception as e:
			if settings.DEBUG: print(e)

	return JsonResponse({ 'ref_result' : render_to_string('reviewer/partials/course/course-refs.html', { 'references': retjson['obj'] , 'request': request, 'user' : request.user }).strip() })
