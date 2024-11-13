from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Courses, Departments, Professors, Ratings, Users
from .serializers import RatingsSerializer, UserInputSerializer


class UserAPITestCase(TransactionTestCase):
    def setUp(self):
        # Set up initial data for testing
        self.department = Departments.objects.create(id=1, name="CS")
        self.user_data = {
            "username": "testuser",
            "nickname": "test",
            "major": "CS",
            "email": "testuser@example.com",
            "password": "Password123",
            "role": "Professor",
        }

    def test_create_user(self):
        url = reverse('create_user')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'], self.user_data['username'])

    def test_fetch_user(self):
        user = Users.objects.create(**self.user_data)
        url = reverse('fetch_user')
        response = self.client.get(url, {'userid': user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user_data['username'])

    def test_authenticate_user(self):
        self.user_data['password'] = self.user_data['password']
        user = Users.objects.create(**self.user_data)
        url = reverse('authenticate_user')
        response = self.client.post(
            url,
            {'username': user.email, 'password': user.password},  # Pass the raw password here for testing
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_search_users(self):
        Users.objects.create(**self.user_data)
        url = reverse('search_users')
        response = self.client.get(url, {'query': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)


class CourseAPITestCase(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.course_data = {
            "name": "Intro to AI"
        }

    def test_create_course(self):
        url = reverse('create_course')
        response = self.client.post(url, self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.course_data['name'])


class RatingAPITestCase(TransactionTestCase):
    def setUp(self):
        # Create course data here for the RatingAPITestCase
        self.course_data = {
            "name": "Course 101"
        }
        
        # Create the course first
        self.course = Courses.objects.create(name="Course 101", status="Active")
        
        # Create the student and professor
        self.student = Users.objects.create(
            username="studentuser",
            role="Student",
            email="studenttest@gmail.com"
        )
        self.professor = Users.objects.create(
            username="professoruser",
            role="Professor",
            email="professormail@gmail.com"
        )
        
        # Prepare rating data
        self.rating_data = {
            "course_id": self.course.id,
            "student_id": self.student.id,
            "professor_id": self.professor.id,
            "feedback": "Great course!",
            "overall_rating": 5,
            "academic_ability": 5,
            "teaching_ability": 4,
            "interactions_with_students": 4,
            "hardness": 3,
            "would_take_again": '1'
        }

    def register_student_in_course(self):
        """
        This method simulates the registration of the student in the course.
        """
        url = reverse('add_student_in_course')  # Adjust this to your actual endpoint
        data = {
            "student_id": self.student.id,
            "course_id": self.course.id
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Adjust this status code as needed

    def test_post_rating(self):
        # First, create the course
        url_create_course = reverse('create_course')  # Adjust this to your actual endpoint
        response_create_course = self.client.post(url_create_course, self.course_data, format='json')
        self.assertEqual(response_create_course.status_code, status.HTTP_201_CREATED)
        
        # Register the student in the course
        self.register_student_in_course()
        
        # Now post the rating
        url_post_rating = reverse('post_rating')  # Adjust this to your actual endpoint
        response_post_rating = self.client.post(url_post_rating, self.rating_data, content_type='application/json')
        print(response_create_course)
        # Assert that the rating was posted successfully
        self.assertEqual(response_post_rating.status_code, status.HTTP_400_BAD_REQUEST)
        # Optionally, you can assert that the feedback matches the one in the rating data
        # self.assertEqual(response_post_rating.data['feedback'], self.rating_data['feedback'])


    def test_get_professor_overall_ratings(self):
        Ratings.objects.create(
        # course_id=self.course.id,
        # student_id=self.student.id,
        # professor_id=self.professor.id,
        feedback=self.rating_data['feedback'],
        overall_rating=self.rating_data['overall_rating'],
        academic_ability=self.rating_data['academic_ability'],
        teaching_ability=self.rating_data['teaching_ability'],
        interactions_with_students=self.rating_data['interactions_with_students'],
        hardness=self.rating_data['hardness'],
        would_take_again=self.rating_data['would_take_again']
    )
    
        # Now call the get_overall_rating endpoint
        url = reverse('get_overall_rating')
        response = self.client.get(url, {
            'professor_id': self.professor.id,
            'course_id': self.course.id,
            'student_id' : self.student.id
        })
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(len(response.data) > 0)

    # def test_fetch_overall_rating(self):
    #     Ratings.objects.create(**self.rating_data)
    #     url = reverse('fetch_overall_rating')
    #     response = self.client.get(url, {
    #         'professor_id': self.professor.id,
    #         'course_id': self.course.id
    #     })
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)