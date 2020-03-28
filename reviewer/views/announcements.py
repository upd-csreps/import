
import json
from ..models import Announcement
from django.shortcuts import render


def announcement_view(request, id):

	announcement = Announcement.objects.get(id=id)

	context = {
		'announcement' : announcement,
		'announcement_json' : json.dumps(announcement.body),
	}

	return render(request, 'reviewer/announcement.html', context)


def announcements(request):

	announcements = Announcement.objects.order_by('-datepost')
	
	context = {'announcements': announcements}
	return render(request, 'reviewer/announcement-list.html', context)
