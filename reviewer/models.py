from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Course(models.Model):
	name = models.CharField("Course Name", max_length=20)
	code = models.CharField("Course Code", max_length=10)
	number = models.CharField("Course Number", max_length=10)
	title = models.CharField("Course Title", max_length=50)
	description = models.TextField("Course Description", blank=True)
	old_curr = models.BooleanField("Pre-2018 Curriculum Exclusive?", default=False)
	visible = models.BooleanField("Visible?", default=True)
	prereqs = models.ManyToManyField('self', blank=True, default=None)
	coreqs = models.ManyToManyField('self', blank=True, default=None)
	lastupdated = models.DateTimeField("Last Updated", default=timezone.now)

	def __str__(self):
		return	'{}'.format(self.name)

class Language(models.Model):

	name = models.CharField(max_length=20)
	image = models.CharField(max_length=100)

	def __str__(self):
		return	'{}'.format(self.name)

class ImportUser(AbstractUser):

	username = models.CharField("Username", max_length=30, primary_key=True)
	first_name = models.CharField("First Name", max_length=30)
	middle_name = models.CharField("Middle Name", max_length=30, null=True)
	last_name = models.CharField("Last Name", max_length=30)
	suffix = models.CharField("Suffix", max_length=10, blank=True, null=True)
	#password = models.CharField("Password", max_length=160)
	studentnum = models.PositiveIntegerField("Student Number", null=True)
	email = models.EmailField("E-mail", max_length=60)
	course = models.CharField("Course/Degree Program", max_length=60)
	
	is_superuser = models.BooleanField("Is SuperUser?", default=False)
	exp = models.PositiveIntegerField("Experience Points", default=0)
	prof_pic = models.CharField("Profile Pic URL", max_length= 100)

	fave_lang = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Favorite Language")

	def __str__(self):
		return	'{} - {}, {}'.format(self.username, self.last_name, self.first_name)


class Comment(models.Model):

	course_attr = models.ForeignKey(Course, on_delete=models.CASCADE)
	user_attr = models.ForeignKey(ImportUser, on_delete=models.CASCADE)
	body = models.CharField(max_length=140)
	image_url = models.CharField(max_length=100)


	def __str__(self):
		return	'Comment #{} - {}, {}'.format(self.id, self.course_attr, self.body[0:10])

class Reply(models.Model):

	comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
	user_attr = models.ForeignKey(ImportUser, on_delete=models.CASCADE)
	body = models.CharField(max_length=140)
	image_url = models.CharField(max_length=100)


	def __str__(self):
		return	'Reply to Comment #{} - {}, {}'.format(self.comment.id, self.id, self.course_attr, self.body[0:10])

class Announcement(models.Model):

	title = models.CharField(max_length=30)
	body = models.TextField()
	poster = models.ForeignKey(ImportUser, on_delete=models.CASCADE)
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
		return	'{}'.format(self.name)