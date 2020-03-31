
from ..models import BugReport
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from ..custom import *

# Create your views here.

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
