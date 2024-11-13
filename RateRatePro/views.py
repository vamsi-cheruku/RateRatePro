import json
# from .elasticsearch import *
import logging

from better_profanity import profanity
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Case, Count, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import esconsts
from .models import *
from .opensearch.opensearch import *
from .serializers import *


@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        print("*****CREATE USER VIEW CALLED *******")
        serializer = UserInputSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()  # Insert data into User table
            
            match user.role:
                case 'Student':
                    pass
                case 'Professor':
                    # Insert the Professor's data into the Professors table
                    # department_id = request.data.get('department_id')
                    department_id = 1 # default department id
                    # Ensure department_id is provided
                    if not department_id:
                        return Response({'error': 'Department ID is required for Professors.'},status=status.HTTP_400_BAD_REQUEST)

                    department = Departments.objects.get(id=department_id)
                    # profid = Users.objects.g et(user.id)
                    professor = Professors.objects.create(
                        id = user,
                        department_id = department,
                        overall_rating = request.data.get('overall_rating')  # Initial rating is null or you can set a default value
                    )
                    professor.save()  # Save the Professor data in the Professors table
            
            try:
                # Create a new document for ElasticSearch
                user_document = {
                    "userid": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "major": user.major,
                    "email": user.email,
                    "role": user.role,
                }
                
                index_name = esconsts.USER_INDEX
                # create_user_index(index_name)
                create_user_index(index_name)
                index_user(index_name, user.id, user_document)  # Insert data into Elasticsearch index
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': 'Something went wrong while creating user'}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.errors:
            error_message = list(serializer.errors.values())[0][0]
        else:
            error_message = "Unknown error occurred"

        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

            
@api_view(['GET'])
def fetch_user(request):
    userid = request.query_params.get('userid')
    
    if userid:
        try:
            user = Users.objects.get(id=userid)
            serializer = UserResponseSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            # Catch validation errors and format the response
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def authenticate_user(request):
    print("********* AUTHENTICATE USER VIEW CALLED ***********")
    username = request.data.get('username')
    password = request.data.get('password')
    # Ensure both username and password are provided
    if not username or not password:
        return Response({'error': 'Username or password not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Check if a user with the provided email (username) exists
        user = Users.objects.get(email=username)
        
        # Directly compare the stored plain text password (since hashing is not being used)
        if user.password == password:
            serializer = UserInputSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    except Users.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
        
# Function to search users for the given search query
@api_view(['GET'])
def search_users(request):
    search_query = request.query_params.get('query', '')
    filters = request.query_params.get('filters')
    if search_query:
        # Call Elasticsearch to perform the search
        search_results = client.search(
            index=esconsts.USER_INDEX,
            body = {
                "query": {
                    "bool": {
                        "must": {
                            "multi_match": {
                                "query": "*" + search_query + "*", # wild card for partial matches 
                                "fields": ["username", "nickname", "email"],  # Adjust fields as necessary
                                "type": "best_fields",  # Allows fuzziness
                                "fuzziness": "AUTO",  # Fuzzy matching for typo tolerance
                                "operator": "and"  # Ensures all words are matched
                            }
                        },
                        #! Filter to fetch only professors
                        "filter": {
                            "term": {
                                "role": "Professor"  # Filter by role
                            }
                        }
                    }
                }
            }
        )
        
        # Format the search results for the response
        users = []
        for hit in search_results['hits']['hits']:
            user_data = hit['_source']
            user_data['userid'] = hit['_id']
            users.append(user_data)
        
        return Response(users, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def create_course(request):
    if request.method == 'POST':
        serializer = CourseSerializer(data = request.data)
        if serializer.is_valid():
            course = serializer.save()  # Insert data into Courses table
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        error_message = list(serializer.errors.values())[0][0]
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_student_in_course(request):
    print("********** REGISTER STUDENT IN COURSE API VIEW CALLED *************")
    if request.method == 'POST':
        body = json.loads(request.body)
        course_id = body.get('course_id')
        student_id = body.get('student_id')
        
        # Check if student is already enrolled in the course
        if StudentCourses.objects.filter(student_id=student_id, course_id=course_id).exists():
            return Response({'error': 'Student is already enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Insert student in CourseStudents table
        serializer = StudentCourseSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()  # Insert data into StudentCourses table
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        error_message = list(serializer.errors.values())[0][0]
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_department(request):
    if request.method == 'POST':
        serializer = DepartmentSerializer(data = request.data)
        if serializer.is_valid():
            department = serializer.save()  # Insert data into Departments table
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        error_message = list(serializer.errors.values())[0][0]
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def post_rating(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        course_id = body.get('course_id')
        student_id = body.get('student_id')
        professor_id = body.get('professor_id')
        feedback = body.get('feedback', '')  # Assuming you have a comment field in the request body

        # Required fields
        required_fields = ['course_id', 'student_id', 'professor_id']

        # Check for missing fields
        missing_fields = [field for field in required_fields if body.get(field) is None]
        if missing_fields:
            return Response({'error': f"{', '.join(missing_fields)} is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if student is registered in the course
        if not StudentCourses.objects.filter(student_id=student_id, course_id=course_id).exists():
            return Response({'error': 'You must be registered in this course to give a rating.'}, status=status.HTTP_400_BAD_REQUEST)

        # Profanity check
        if profanity.contains_profanity(feedback):
            return Response({'error': 'Your comment contains inappropriate language.'}, status=status.HTTP_400_BAD_REQUEST)

        # Insert rating in Ratings table
        serializer = RatingsSerializer(data=body)  # Use body instead of request.data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        error_message = list(serializer.errors.values())[0][0]
        print("########## error message: "+error_message)
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_professor_ratings(request):
    try:
        body = json.loads(request.body)
        professor_id = body.get('professor_id')
        course_id = body.get('course_id')
        
        # Filter the Professor ratings by professor_id and course_id
        ratings = Ratings.objects.filter(professor_id=professor_id, course_id=course_id)
        
        # If no ratings found, return an error message
        if not ratings.exists():
            return Response({'error': 'No ratings found for the given professor and course.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the ratings data
        serializer = RatingsSerializer(ratings, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def fetch_overall_rating(request):
    professor_id = request.GET.get('professor_id')
    course_id = request.GET.get('course_id')

    if professor_id:
        try:
            # Filter ratings for professor, optionally by course
            ratings = Ratings.objects.filter(professor_id=professor_id)
            if course_id:
                ratings = ratings.filter(course_id=course_id)

            if ratings.exists():
                # Aggregate ratings
                aggregated_data = ratings.aggregate(
                    overall_rating_avg=Avg('overall_rating'),
                    would_take_again_count_1=Count(Case(When(would_take_again='1', then=1))),
                    would_take_again_count_0=Count(Case(When(would_take_again='0', then=1))),
                    academic_ability_avg=Avg('academic_ability'),
                    teaching_ability_avg=Avg('teaching_ability'),
                    interactions_with_students_avg=Avg('interactions_with_students'),
                    hardness_avg=Avg('hardness')
                )

                feedback_list = list(ratings.values_list('feedback', flat=True)[:3])
                would_take_again_counts = {
                    '1': aggregated_data['would_take_again_count_1'],
                    '0': aggregated_data['would_take_again_count_0']
                }
                
                # Fetch related courses as a list of dictionaries
                courses = list(Courses.objects.filter(
                    id__in=ProfessorCourses.objects.filter(professor_id=professor_id).values('course_id')
                ).values('id', 'name', 'status'))

                # Combine aggregated data and additional info
                response_data = {
                    'overall_rating': round(aggregated_data['overall_rating_avg'], 2),
                    'would_take_again': would_take_again_counts,
                    'academic_ability': round(aggregated_data['academic_ability_avg'], 2),
                    'teaching_ability': round(aggregated_data['teaching_ability_avg'], 2),
                    'interactions_with_students': round(aggregated_data['interactions_with_students_avg'], 2),
                    'hardness': round(aggregated_data['hardness_avg'], 2),
                    'feedback': feedback_list,
                    'courses': courses  # Pass list of dictionaries directly
                }

                # Serialize response data
                serializer = ProfessorRatingsSerializer(response_data)
                return JsonResponse(response_data, safe=False, status=200)

            else:
                return Response({'error': 'No ratings found for this professor'}, status=404)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    return Response({'error': 'professor_id parameter is required'}, status=400)
@api_view(['GET'])
def compare_professors(request):
    professor_id1 = request.GET.get('professor_id1')  # First professor ID
    professor_id2 = request.GET.get('professor_id2')  # Second professor ID

    if professor_id1 and professor_id2:
        try:
            # Helper function to get aggregated data for a professor
            def get_professor_data(professor_id):
                ratings = Ratings.objects.filter(professor_id=professor_id)
                if ratings.exists():
                    aggregated_data = ratings.aggregate(
                        overall_rating_avg=Avg('overall_rating'),
                        would_take_again_count_1=Count(Case(When(would_take_again='1', then=1))),
                        would_take_again_count_0=Count(Case(When(would_take_again='0', then=1))),
                        academic_ability_avg=Avg('academic_ability'),
                        teaching_ability_avg=Avg('teaching_ability'),
                        interactions_with_students_avg=Avg('interactions_with_students'),
                        hardness_avg=Avg('hardness')
                    )
                    feedback_list = list(ratings.values_list('feedback', flat=True)[:3])
                    would_take_again_counts = {
                        '1': aggregated_data['would_take_again_count_1'],
                        '0': aggregated_data['would_take_again_count_0']
                    }
                    courses = Courses.objects.filter(
                        id__in=ProfessorCourses.objects.filter(professor_id=professor_id).values('course_id')
                    ).values_list('name', flat=True)

                    return {
                        'overall_rating': round(aggregated_data['overall_rating_avg'], 2),
                        'would_take_again': would_take_again_counts,
                        'academic_ability': aggregated_data['academic_ability_avg'],
                        'teaching_ability': aggregated_data['teaching_ability_avg'],
                        'interactions_with_students': aggregated_data['interactions_with_students_avg'],
                        'hardness': aggregated_data['hardness_avg'],
                        'feedback': feedback_list,
                        'courses': courses
                    }
                else:
                    return None

            # Get data for both professors
            data_prof1 = get_professor_data(professor_id1)
            data_prof2 = get_professor_data(professor_id2)

            if data_prof1 and data_prof2:
                response_data = {
                    professor_id1: data_prof1,
                    professor_id2: data_prof2
                }
                return Response(response_data, status=200)
            else:
                return Response({'error': 'One or both professors have no ratings.'}, status=404)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    return Response({'error': 'Both professor_id1 and professor_id2 parameters are required'}, status=400)

@api_view(['POST'])
def assign_course_to_professor(request):
    serializer = AssignCourseSerializer(data=request.data)
    
    if serializer.is_valid():
        professor_id = serializer.validated_data['professor_id']
        course_id = serializer.validated_data['course_id']

        # Retrieve the Professor and Course instances
        try:
            professor_id = Professors.objects.get(id=professor_id)
            course_id = Courses.objects.get(id=course_id)
        except Professors.DoesNotExist:
            return Response({'error': 'Professor not found'}, status=status.HTTP_404_NOT_FOUND)
        except Courses.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the assignment already exists
        if ProfessorCourses.objects.filter(professor_id=professor_id, course_id=course_id).exists():
            return Response({'error': 'This course is already assigned to the professor'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the assignment
        ProfessorCourses.objects.create(professor_id=professor_id, course_id=course_id)
        
        return Response({'message': 'Course assigned to professor successfully'}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_ratings_by_student(request):
    student_id = request.query_params.get('student_id')  # Extract student_id from query parameters
    if not student_id:
        return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch ratings for the given student_id
        ratings = Ratings.objects.filter(student_id=student_id)
        # Serialize the ratings data
        serializer = RatingsSerializer(ratings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Ratings.DoesNotExist:
        return Response({"message": "No ratings found for the student."}, status=status.HTTP_404_NOT_FOUND)

# @api_view(['POST'])
# def password_reset(self, request):
#     serializer = PasswordResetSerializer(data=request.data)
#     if serializer.is_valid():
#         email = serializer.validated_data['email']
#         new_password = serializer.validated_data['new_password']
#         try:
#             user = Users.objects.get(Email=email)
#             user.Password = make_password(new_password)  # Hash the new password
#             user.save()
#             return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
#         except Users.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def professor_courses(request):
    # Get the professor_id from query parameters
    professor_id = request.query_params.get('professor_id')

    if not professor_id:
        return Response({"error": "Professor ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        courses = list(Courses.objects.filter(
                    id__in=ProfessorCourses.objects.filter(professor_id=professor_id).values('course_id')
                ).values('id', 'name', 'status'))
        
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Professors.DoesNotExist:
        return Response({"error": "Professor not found"}, status=status.HTTP_404_NOT_FOUND)