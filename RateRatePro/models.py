from django.db import models
from django.utils import timezone


class Courses(models.Model):
    STATUS_CHOICE = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=8, choices=STATUS_CHOICE, default='Active')

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Courses'


class Departments(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Departments'
    

class Ratings(models.Model):
    COMMENT_EDIT_STATUS = [
        ('0', '0'),
        ('1', '1')
    ]
    id = models.AutoField(primary_key=True)
    overall_rating = models.FloatField(null=True, blank=True, db_column='OverallRating')
    would_take_again = models.FloatField(null=True, blank=True, db_column='WouldTakeAgain')
    academic_ability = models.FloatField(null=True, blank=True, db_column='AcademicAbility')
    teaching_ability = models.FloatField(null=True, blank=True, db_column='TeachingAbility')
    interactions_with_students = models.FloatField(null=True, blank=True, db_column='InteractionsWithStudents')
    hardness = models.FloatField(null=True, blank=True, db_column='Hardness')
    feedback = models.CharField(max_length=500, null=True, blank=True, db_column='Feedback')
    is_edited = models.CharField(max_length=50, blank = True, choices=COMMENT_EDIT_STATUS, db_column='IsEdited', default='0')
    timestamp = models.DateTimeField(auto_now_add=True, db_column='TimeStamp')
    
    student_id = models.ForeignKey('Users', on_delete=models.SET_NULL, null=True, blank=True, db_column='StudentID')
    course_id = models.ForeignKey('Courses', on_delete=models.SET_NULL, null=True, blank=True, db_column='CourseID')
    professor_id = models.ForeignKey('Professors', on_delete=models.SET_NULL, null=True, blank=True, db_column='ProfID')

    def __str__(self):
        return f'Rating {self.id} by {self.student_id} for {self.professor_id}'
    
    class Meta:
        db_table = 'Ratings'


class StudentCourses(models.Model):
    course_id = models.ForeignKey('Courses', on_delete=models.CASCADE, db_column="CourseID")
    student_id = models.ForeignKey('Users', on_delete=models.CASCADE, db_column="StudentID")

    class Meta:
        db_table = 'StudentCourses'
        unique_together = ('course_id', 'student_id')  # Ensures that each student can only enroll in a course once

    def __str__(self):
        return f'{self.student_id.username} enrolled in {self.course.name}'


class Users(models.Model):
    ROLE = [
        ('Student', 'Student'),
        ('Professor', 'Professor'),
        ('Non-Student', 'Non-Student'),
    ]
    id = models.AutoField(primary_key=True, db_column='Id')  # Map 'userid' to the 'Id' column
    username = models.CharField(max_length=100, db_column='UserName')  # Map 'username' to 'UserName'
    nickname = models.CharField(max_length=50, null=True, blank=True, db_column='NickName')
    major = models.CharField(max_length=50, null=True, blank=True, db_column='Major')
    email = models.EmailField(max_length=100, unique=True, db_column='Email')
    password = models.CharField(max_length=12, null=True, blank=True, db_column='Password')
    role = models.CharField(max_length=20, choices=ROLE, default='Non-Student', db_column='Role')

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'Users'

class Professors(models.Model):
    id = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True, db_column='Id')
    # id = models.ForeignKey(Users, on_delete=models.CASCADE, primary_key=True, db_column='Id')  # Foreign key to Users
    department_id = models.ForeignKey(Departments, null=True, on_delete=models.SET_NULL, blank=True, db_column='DepartmentID')  # Foreign key to Departments
    overall_rating = models.FloatField(null=True, db_column='OverallRating')  # OverallRating can be null if not set

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Professors'
        # unique_together = ('department_id', 'id')
        

class ProfessorCourses(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professors, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ProfessorCourses'
        unique_together = ('course', 'professor')  # To ensure the uniqueness of the combination

    def __str__(self):
        return f'{self.professor.name} teaches {self.course.name}'
