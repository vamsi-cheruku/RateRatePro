from rest_framework import serializers
from .models import *

class UserInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        
class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'nickname', 'major', 'email', 'role']  # fields to include
        extra_kwargs = {
            'password': {'write_only': True}  # This ensures password is not included in the response
        }

class ProfessorInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professors
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = '__all__'

class StudentCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourses
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = '__all__'
class RatingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ratings
        fields = '__all__'
