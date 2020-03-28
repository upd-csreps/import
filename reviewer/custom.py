from django.core.mail import get_connection, EmailMultiAlternatives

from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2 import service_account
import io

# Insert Custom Functions Here

def send_mass_html_mail(datatuple, fail_silently=False, auth_user=None, auth_password=None, connection=None):
	"""
	Given a datatuple of (subject, message, from_email, recipient_list), send
	each message to each recipient list. Return the number of emails sent.

	If from_email is None, use the DEFAULT_FROM_EMAIL setting.
	If auth_user and auth_password are set, use them to log in.
	If auth_user is None, use the EMAIL_HOST_USER setting.
	If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

	Note: The API for this method is frozen. New code wanting to extend the
	functionality should use the EmailMessage class directly.
	"""

	connection = connection or get_connection(
		username=auth_user,
		password=auth_password,
		fail_silently=fail_silently,
	)

	messages = []
	for subject, message, html, sender, recipient in datatuple:
		message = EmailMultiAlternatives(subject, message, sender, recipient, connection=connection)

		if html:
			message.attach_alternative(html, 'text/html')

		messages.append(message)

	return connection.send_messages(messages)



def gdrive_import_folderID():
	return "1dc3LnAdcy0AU4i2K4hoVr9_Oaz64zWFh"

def gdrive_import_exportURL():
	return "https://drive.google.com/uc?export=view&id="

def gdrive_connect(api_creds=settings.GOOGLE_API_CREDS, api_scopes=settings.GOOGLE_API_SCOPES ):

	creds = service_account.Credentials.from_service_account_info(api_creds, scopes=api_scopes)

	if settings.DEBUG == True:
		print("Connecting to Google Drive...\n")

	service = build('drive', 'v3', credentials=creds)

	return service 


def gdrive_delete_file(service, fileID):

	try:
		file = service.files().delete(fileId=fileID).execute()
	except Exception as e: 
		print(e)
		return False

	return True

def gdrive_create_file(service, file_metadata,  mimetype):

	file = service.files().create(body=file_metadata, fields='id').execute()
	return file.get('id')

def gdrive_get_file(service, file_metadata,  mimetype):

	try:
		file = service.files().get(fileId=fileID).execute()
	except Exception as e: 
		print(e)
		return False

	return True


def gdrive_upload_file(service,image_dir, file_metadata,  mimetype):

	media = MediaFileUpload(image_dir, mimetype=mimetype, resumable=True)

	file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
	return file.get('id')

def gdrive_download_file(service, fileID):

	req = service.files().get_media(fileId=file_id)
	fh = io.BytesIO()
	downloader = MediaIoBaseDownload(fh, req)
	done = False
	while done is False:
		status, done = downloader.next_chunk()
		print("Download " + str(int(status.progress() * 100)) + '%')

	print(fh.getvalue())	

	return fh

def gdrive_list_meta(service, query=None, pageSize=10):

	returned_list = {}

	# Call the Drive v3 API

	page_ct = 1
	page_token = None
	while True:
		results = service.files().list(pageSize=pageSize,
	    								q=query,
	    								fields='nextPageToken, files(id, name, mimeType)',
	                                    pageToken=page_token).execute()
		
		items = results.get('files', [])

		if not items:
			print('No files found.')
		else:
			if (pageSize != None):
				print('Page ' + page_ct + ' \n')

			print('Files:')
			for item in items:
				print(u'{0} ({1})\t {2}'.format(item['name'], item['id'], item['mimeType']))
				returned_list[ item['id'] ] = [item['name'], item['mimeType']]

		page_token = results.get('nextPageToken', None)

		if page_token is None:
			break
		else:
			page_ct = page_ct+1

	return returned_list


def gdrive_list_meta_folders(service, query=None, pageSize=10):

	if query != None:
		query = query + "and mimeType = 'application/vnd.google-apps.folder'"
	else:
		query = "mimeType = 'application/vnd.google-apps.folder'"

	return gdrive_list_meta(service, query=query, pageSize=pageSize)

def gdrive_list_meta_files(service, query=None, pageSize=10):
	if query != None:
		query = query + "and mimeType != 'application/vnd.google-apps.folder'"
	else:
		query = "mimeType != 'application/vnd.google-apps.folder'"

	return gdrive_list_meta(service, query=query, pageSize=pageSize)


def gdrive_list_meta_children(service, folderID=None, query="", pageSize=None):

	if folderID == None:
		folderID = gdrive_import_folderID()

	if query == "":
		query = "\'"+ folderID + "\' in parents"
	else:
		query = "\'"+ folderID + "\' in parents and " + query
	return gdrive_list_meta(service, query, pageSize=pageSize)

