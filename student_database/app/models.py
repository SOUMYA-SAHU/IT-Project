from django.db import models
from django.contrib.auth.models import User

class Details(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    regno = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    gender = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=15)
    branch = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
from django.db import models

class Course(models.Model):
    course_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=10, unique=True)
    dept = models.CharField(max_length=50)

    def __str__(self):
        return self.course_code

class StudentCourse(models.Model):
    regno = models.ForeignKey(Details, on_delete=models.CASCADE)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    attendance = models.FloatField(default=0)  # Assuming it's a percentage
    course_marks = models.FloatField(default=0)  # Assuming it's a numeric value

    def __str__(self):
        return f"Reg No: {self.regno}, Course Code: {self.course_code}"
    
