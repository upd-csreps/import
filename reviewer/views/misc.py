
from ..models import BugReport
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

import json

from ..custom import *

# Create your views here.

def bug_report_list(request):

	mybugreports = BugReport.objects.filter(user=request.user).order_by('-lastupdated')
	
	context = {'my_bugreports': mybugreports}
	return render(request, 'reviewer/user/user-bug_report.html', context)

def google_test(request):

	service = gdrive_connect()

	retjson = {'obj': gdrive_list_meta_children(service)}

	return HttpResponse( json.dumps(retjson) )
