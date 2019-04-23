from django.db import models

# Create your models here.
class Course(models.Model):
	name = models.CharField("Course Name", max_length=20)
	code = models.CharField("Course Code", max_length=10)
	number = models.CharField("Course Number", max_length=10)
	title = models.CharField("Course Title", max_length=50)
	description = models.TextField("Course Description", blank=True)
	old_curr = models.BooleanField("Pre-2018 Curriculum Exclusive?", default=False)

	def __str__(self):
		return	'{}'.format(self.name)