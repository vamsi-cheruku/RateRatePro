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

class ProfessorRatingsSerializer(serializers.Serializer):
    overall_rating = serializers.FloatField()
    would_take_again = serializers.DictField(child=serializers.IntegerField())
    academic_ability = serializers.FloatField()
    teaching_ability = serializers.FloatField()
    interactions_with_students = serializers.FloatField()
    hardness = serializers.FloatField()
    feedback = serializers.ListField(child=serializers.CharField())
    courses = serializers.ListField(child=serializers.CharField())

    def create(self, validated_data):
        # Logic for creating a new entry if needed (optional for this use case)
        return validated_data

    def update(self, instance, validated_data):
        # Logic for updating an entry if needed (optional for this use case)
        return instance

class AssignCourseSerializer(serializers.Serializer):
    professor_id = serializers.IntegerField()
    course_id = serializers.IntegerField()

    def validate_professor_id(self, value):
        if not Professors.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid professor ID")
        return value

    def validate_course_id(self, value):
        if not Courses.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid course ID")
        return value
    
class ProfessorRatingsComparisonSerializer(serializers.Serializer):
    professor_1 = serializers.DictField(child=serializers.FloatField(), required=True)
    professor_2 = serializers.DictField(child=serializers.FloatField(), required=True)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password =  serializers.CharField(required=True, min_length=8, max_length=12)
    
    def validate_email(self, value):
        if not Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("Invalid email")
        return value