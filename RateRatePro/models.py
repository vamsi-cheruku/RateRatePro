from django.db import models

class Users(models.Model):
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
    
    userid = models.AutoField(primary_key=True, db_column='Id')
    username = models.CharField(max_length=100, db_column='UserName')
    nickname = models.CharField(max_length=50, null=True, blank=True, db_column='NickName')
    major = models.CharField(max_length=100, null=True, blank=True, db_column='Major')
    email = models.EmailField(unique=True, db_column='Email')
    password = models.CharField(max_length=12, db_column='Password')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=NON_STUDENT, db_column='Role')
    
    class Meta:
        db_table = 'Users'  # Connect to User table

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