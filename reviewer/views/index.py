import json
from ..models import Announcement
from django.shortcuts import render

# Index View

def index(request):
	announcements = Announcement.objects.order_by('-datepost')[0:3]
	announcements_json = []

	for announcement in announcements:
		announcements_json.append(json.dumps(announcement.body))

	context = { 
		'announcements': announcements, 
		'announcements_json' : announcements_json,
		'is_home': True
	}

	return render(request, 'reviewer/index.html', context)
