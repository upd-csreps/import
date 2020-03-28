
from ..models import BugReport
from django.conf import settings
from django.shortcuts import render

from googleapiclient.discovery import build
from google.oauth2 import service_account


# Create your views here.

def bug_report_list(request):

	mybugreports = BugReport.objects.filter(user=request.user).order_by('-lastupdated')
	
	context = {'my_bugreports': mybugreports}
	return render(request, 'reviewer/user/user-bug_report.html', context)


def google_test(request):

	SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
	creds = service_account.Credentials.from_service_account_info(settings.GOOGLE_API_CREDS, scopes=SCOPES)

	print("Connecting to Google Drive...\n")
	service = build('drive', 'v3', credentials=creds)

	file_metadata = {
	    'name': 'media',
	    'mimeType': 'application/vnd.google-apps.folder'
	}
	file = drive_service.files().create(body=file_metadata,
	                                    fields='id').execute()
	print('Folder ID: ' + file.get('id'))


	# Call the Drive v3 API
	results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
	items = results.get('files', [])

	if not items:
		print('No files found.')
	else:
		print('Files:')
	for item in items:
		print(u'{0} ({1})'.format(item['name'], item['id']))

	return None

