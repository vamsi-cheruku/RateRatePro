from django.db import models

class User(models.Model):
    STUDENT = 'Student'
    NON_STUDENT = 'Non-Student'
    PROFESSOR = 'Professor'
    ADMIN = 'Admin'
    
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (NON_STUDENT, 'Non-Student'),
        (ADMIN, 'Admin'),
        (PROFESSOR, 'Professor'),
    ]
    
    userID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50, null=True, blank=True)
    major = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=12)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=NON_STUDENT)
    
    class Meta:
        db_table = 'User'  # Connect to User table

    def __str__(self):
        return self.name

class Courses(models.Model):
    courseID = models.AutoField(primary_key=True)
    courseName = models.CharField(max_length=100)
    courseStatus = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'Courses'  # Connect to Courses table
        
    def __str__(self):
        return self.courseName