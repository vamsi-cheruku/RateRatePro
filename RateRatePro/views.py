from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
import json
from .constants import esconsts
from .elasticsearch import *

@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        serializer = UserInputSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()  # Insert data into User table
            
            match user.role:
                case 'Student':
                   pass
                case 'Professor':
                    # Insert the Professor's data into the Professors table
                    department_id = request.data.get('department_id')
                    
                    # Ensure department_id is provided
                    if not department_id:
                        return Response({'error': 'Department ID is required for Professors.'},status=status.HTTP_400_BAD_REQUEST)

                    department = Departments.objects.get(id=department_id)
                    # profid = Users.objects.get(user.id)
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
                create_index(index_name)
                index_user(index_name, user.id, user_document)  # Insert data into Elasticsearch index
                    
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print("Error while indexing user document in Elastic Search")
                # return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        error_message = list(serializer.errors.values())[0][0]
        print("Error while creating user document: ")
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
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            # Catch validation errors and format the response
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def authenticate_user(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        
        # logic to check if username/email is already in use and then check if password is correct
        if username and password:
            try:
                user = Users.objects.get(email = username)
                if user.password == password:
                    serializer = UserInputSerializer(user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
            except Users.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Username or password not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
        
# Function to search users for the given search query
@api_view(['GET'])
def search_users(request):
    search_query = request.query_params.get('query', '')
    filters = request.query_params.get('filters')
    if search_query:
        # Call Elasticsearch to perform the search
        search_results = es.search(
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
                        # "filter": {
                        #     "term": {
                        #         "role": "Professor"  # Filter by role
                        #     }
                        # }
                    }
                }
            }
        )
        
        # Format the search results for the response
        print("SEARCH HITS FOR QUERY ", search_query, " IS : ", search_results)
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
        course_id = body.get('course_id') # Course ID to which the rating pertains
        student_id =  body.get('student_id') # Student ID who is giving the rating
        professor_id =  body.get('professor_id') # Professor ID being rated
        
        # Required fields
        required_fields = ['course_id', 'student_id', 'professor_id']
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if body.get(field) is None]
        if missing_fields:
            return Response({'error': f"{', '.join(missing_fields)} is required."}, status=status.HTTP_400_BAD_REQUEST)
    
        # Check if student is registed in the course
        if not StudentCourses.objects.filter(student_id=student_id, course_id=course_id).exists():
            return Response({'error': 'You must be registered in this course to give a rating.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Insert rating in Ratings table
        serializer = RatingsSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()  # Insert data into Ratings table
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        error_message = list(serializer.errors.values())[0][0]
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
            return Response({'error': 'No ratings found for the given professor and course.'}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the ratings data
        serializer = RatingsSerializer(ratings, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
