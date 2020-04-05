from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

# Create your models here.


def course_uploadto(instance, filename):
	return 'course/{0}-{1}/{2}'.format(instance.code, instance.number, filename)


class Course(models.Model):
	name = models.CharField("Course Name", max_length=20, unique=True)
	code = models.CharField("Course Code", max_length=10)
	number = models.CharField("Course Number", max_length=10)
	number_len = models.PositiveSmallIntegerField(default=1)
	title = models.CharField("Course Title", max_length=50)
	description = models.TextField("Course Description", blank=True)
	old_curr = models.BooleanField("Pre-2018 Curriculum Exclusive?", default=False)
	visible = models.BooleanField("Visible?", default=True)
	prereqs = models.ManyToManyField('self', blank=True, default=None, symmetrical=False, related_name="preq")
	coreqs = models.ManyToManyField('self', blank=True, default=None,symmetrical=False , related_name="creq")
	lastupdated = models.DateTimeField("Last Updated", default=timezone.now)

	# image = models.ImageField(verbose_name="Photo", null=True, blank=True, upload_to=course_uploadto)
	imageID = models.CharField("Photo ID", max_length=40, blank=True, null=True, default=None)

	def __str__(self):
		return	'{}'.format(self.name)

	def save(self, *args, **kwargs):
		self.number_len = len(self.number)
		return super(Course, self).save(*args, **kwargs)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['code', 'number'], name='unique codenums')
		]

def language_uploadto(instance, filename):
	return 'language/{0}/{1}'.format(instance.name.lower(), filename)

class Language(models.Model):

	name = models.CharField(max_length=20, unique=True)
	image = models.ImageField(verbose_name="Icon", upload_to=language_uploadto)
	color = models.CharField(max_length=6, default="868686")

	def __str__(self):
		return	'{}'.format(self.name)

'''

def user_uploadto(instance, filename):

	fileex = filename.split('.')[-1]
	return 'users/{0}/image.{1}'.format(instance.username, fileex)

'''

class ImportUser(AbstractUser):

	userID = models.AutoField(primary_key=True)
	username = models.CharField("Username", max_length=30, unique=True)
	first_name = models.CharField("First Name", max_length=30)
	middle_name = models.CharField("Middle Name", max_length=30, blank=True, null=True)

	last_name = models.CharField("Last Name", max_length=30)
	suffix = models.CharField("Suffix", max_length=10, blank=True, null=True)
	#password = models.CharField("Password", max_length=160)

	studentnum = models.PositiveIntegerField("Student Number", null=True)
	show_studentnum = models.BooleanField("Show Student Number", default=True)

	email = models.EmailField("E-mail", max_length=60)
	show_email = models.BooleanField("Show E-mail", default=True)

	course = models.CharField("Course/Degree Program", max_length=60)
	
	is_superuser = models.BooleanField("Is SuperUser?", default=False)
	exp = models.PositiveIntegerField("Experience Points", default=0)
	
	#prof_pic = models.ImageField(verbose_name="Profile Picture", null=True, blank=True, upload_to=user_uploadto)
	prof_picID = models.CharField("Prof Pic ID", max_length=40, blank=True, null=True, default=None)

	fave_lang = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Favorite Language")

	dark_mode = models.BooleanField("Dark Mode", default=False);
	notifications = models.BooleanField("Notifications", default=True);

	USERNAME_FIELD = 'username'

	def __str__(self):
		return	'{} - {}, {}'.format(self.username, self.last_name, self.first_name)


def post_uploadto(instance, filename):
	return 'users/{0}/posts/{1}'.format(instance.user_attr.username, filename)

class Comment(models.Model):

	course_attr = models.ForeignKey(Course, on_delete=models.CASCADE)
	user_attr = models.ForeignKey(ImportUser, on_delete=models.CASCADE)
	body = models.CharField(max_length=150)
	image = models.ImageField(verbose_name="Image", null=True, blank=True, upload_to=post_uploadto)
	date_posted = models.DateTimeField("Date Posted", default=timezone.now)

	def __str__(self):
		return	'Comment #{} - {}, {}'.format(self.id, self.course_attr, self.body[0:10])


class Likes(models.Model):

	comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
	user_attr = models.ForeignKey(ImportUser, on_delete=models.CASCADE)

	def __str__(self):
		return	'Likes to Comment #{} - {}'.format(self.comment.id, self.user_attr)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['comment', 'user_attr'], name='unique like_combo')
		]

def announcement_uploadto(instance, filename):
	return 'announcement/{0}/{1}'.format(instance.id, filename)

class Announcement(models.Model):

	title = models.CharField(max_length=30)
	body = JSONField()
	image = models.ImageField(verbose_name="Image", null=True, blank=True, upload_to=announcement_uploadto)
	poster = models.ForeignKey(ImportUser, on_delete=models.SET_NULL, null=True)
	datepost = models.DateTimeField("Date Posted", default=timezone.now)

	def __str__(self):
		return	'{} - {}, {}'.format(self.title, self.datepost)

class Lesson(models.Model):

	name = models.CharField(max_length=50)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	prereq_lesson = models.ManyToManyField('self', blank=True, default=None)
	verified = models.BooleanField("Verified?", default=False)
	verifier = models.CharField(max_length=50)

	ex_lang = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return	'{}: {}'.format(self.course, self.name)

class Module(models.Model):

	lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
	body = models.TextField()
	custom_code = models.TextField()

	def __str__(self):
		return	'{} - Modules'.format(self.lesson.name)


class Question(models.Model):

	lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
	custom_code = models.TextField()
	qtype = models.CharField(max_length=50)

	def __str__(self):
		return	'{} - Questions'.format(self.lesson.name)

class QuestionBankQ():

	question_root = models.ForeignKey(Question, on_delete=models.CASCADE)
	question_given = models.TextField()
	answer = models.CharField(max_length=30)

	def __str__(self):
		return	'{}'.format(self.question_given)

def partners_uploadto(instance, filename):
	return 'partners/{0}/{1}'.format(instance.name, filename)

class Partners():

	name = models.CharField(max_length=30)
	image = models.ImageField(verbose_name="Logo", null=True,  upload_to=partners_uploadto)
	sponsor = models.BooleanField("Sponsor?", default=False)

	def __str__(self):
		return	'{}'.format(self.name)


class Reference(models.Model):

	title = models.CharField(max_length=50)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	link = models.CharField(max_length=100)

	def __str__(self):
		return	'{}: {}'.format(self.course, self.title)

class LessonStats(models.Model):
	
	lesson_attr = models.ForeignKey(Course, on_delete=models.CASCADE)
	user_attr = models.ForeignKey(ImportUser, on_delete=models.CASCADE)
	date_made = models.DateTimeField("Date", default=timezone.now)
	skips = models.PositiveSmallIntegerField(default=0)
	mistakes = models.PositiveSmallIntegerField(default=0)

	def __str__(self):
		return	'{0} on {1}| {2}'.format(self.user_attr, self.lesson_attr, self.date_made)


class BugReport(models.Model):

	name = models.CharField("Title", max_length=50)
	body = models.CharField("Body", max_length=300)
	status = models.PositiveSmallIntegerField("Status", default=0)
	lastupdated = models.DateTimeField("Last Updated", default=timezone.now)
	admin = models.ForeignKey(ImportUser, null=True, on_delete=models.SET_NULL, related_name="admin")
	user = models.ForeignKey(ImportUser, null=True, on_delete=models.SET_NULL, related_name="user")

	def __str__(self):
		return	'{} [{}]'.format(self.name, self.status)

class SiteSettings(models.Model):

	name = models.CharField(max_length=50)
	body = models.CharField(max_length=300)

	def __str__(self):
		return	'{}'.format(self.name)
