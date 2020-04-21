
from ..models import BugReport
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
import time

from ..custom import *

# Create your views here.

def terms(request):
	context = {}
	return render(request, 'reviewer/legal/terms.html', context)

def privacy(request):
	context = {}
	return render(request, 'reviewer/legal/privacy.html', context)

def disclaimer(request):
	context = {}
	return render(request, 'reviewer/legal/disclaimer.html', context)

def bug_report_list(request):

	mybugreports = BugReport.objects.filter(user=request.user).order_by('-lastupdated')
	
	context = {'my_bugreports': mybugreports}
	return render(request, 'reviewer/user/user-bug_report.html', context)

def google_test(request):

	service = gdrive_connect()

	trashed = gdrive_list_meta(service, query="trashed = true", pageSize=10)

	if trashed != None:
		for i in trashed:
			gdrive_delete_file(service, i)


	retjson = {'obj': gdrive_list_meta_children(service)}

	return JsonResponse(retjson)


def stream_chunks():
	i = 0
	while i < 30:
		yield '{}\n'.format(i)
		time.sleep(1)
		i = i+1


def stream_test(request):
	return StreamingHttpResponse(stream_chunks())
