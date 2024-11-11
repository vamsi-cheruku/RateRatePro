import unittest
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.test import APIRequestFactory
from RateRatePro.views import (
    create_user, fetch_user, authenticate_user, search_users,
    create_course, add_student_in_course, create_department,
    post_rating, fetch_overall_rating
)

factory = APIRequestFactory()

class CreateUserTestCase(unittest.TestCase):
    @patch('RateRatePro.views.UserInputSerializer')
    @patch('RateRatePro.views.Departments')
    @patch('RateRatePro.views.Professors')
    @patch('RateRatePro.views.create_user_index')
    @patch('RateRatePro.views.index_user')
    def test_create_user_professor(self, mock_index_user, mock_create_user_index, mock_professors, mock_departments, mock_serializer):
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.save.return_value = MagicMock(id=1, username="testuser")
        mock_serializer.return_value = mock_serializer_instance

        request = factory.post('http://127.0.0.1:8000/v1/user/create/', {
            "username": "testuser",
            "nickname": "Test",
            "major": "Physics",
            "email": "testuser@example.com",
            "role": "Professor",
            "password": "password"
        }, format='json')

        response = create_user(request)
        print("********"+str(response.status_code))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('RateRatePro.views.UserInputSerializer')
    def test_create_user_invalid_data(self, mock_serializer):
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = False
        mock_serializer_instance.errors = {"username": ["This field is required."]}
        mock_serializer.return_value = mock_serializer_instance

        request = factory.post('/v1/user/create/', {}, format='json')
        response = create_user(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FetchUserTestCase(unittest.TestCase):
    @patch('RateRatePro.views.Users')
    @patch('RateRatePro.views.UserResponseSerializer')
    def test_fetch_user_valid_id(self, mock_serializer, mock_users):
        mock_user_instance = MagicMock()
        mock_users.objects.get.return_value = mock_user_instance
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.data = {
            "username": "testuser",
            "nickname": "Test",
            "major": "Physics",
            "email": "testuser@example.com",
            "role": "Professor"
        }
        mock_serializer.return_value = mock_serializer_instance

        request = factory.get('/v1/user/fetch/', {"userid": 1})
        response = fetch_user(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, mock_serializer_instance.data)

    @patch('RateRatePro.views.Users')
    def test_fetch_user_not_found(self, mock_users):
        # Set side_effect to raise ObjectDoesNotExist directly
        from django.core.exceptions import ObjectDoesNotExist
        mock_users.objects.get.side_effect = ObjectDoesNotExist

        request = factory.get('/v1/user/fetch/', {"userid": 1})
        response = fetch_user(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)


class AuthenticateUserTestCase(unittest.TestCase):
    @patch('RateRatePro.views.Users')
    def test_authenticate_user_valid(self, mock_users):
        mock_user = MagicMock()
        mock_user.password = "password"
        mock_users.objects.get.return_value = mock_user

        request = factory.post('/v1/user/authenticate/', {"username": "test@example.com", "password": "password"}, format='json')
        response = authenticate_user(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('RateRatePro.views.Users')
    def test_authenticate_user_invalid_password(self, mock_users):
        mock_user = MagicMock()
        mock_user.password = "password123"
        mock_users.objects.get.return_value = mock_user

        request = factory.post('/v1/user/authenticate/', {"username": "test@example.com", "password": "password"}, format='json')
        response = authenticate_user(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchUsersTestCase(unittest.TestCase):
    @patch('RateRatePro.views.client')
    def test_search_users(self, mock_client):
        mock_search_results = {'hits': {'hits': [{"_id": "1", "_source": {"username": "testuser"}}]}}
        mock_client.search.return_value = mock_search_results

        request = factory.get('/v1/user/search/', {"query": "test"})
        response = search_users(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['username'], "testuser")


class CreateCourseTestCase(unittest.TestCase):
    @patch('RateRatePro.views.CourseSerializer')
    def test_create_course(self, mock_serializer):
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.save.return_value = MagicMock(id=1, name="Physics", status="Active")
        mock_serializer.return_value = mock_serializer_instance

        request = factory.post('/v1/course/create/', {"name": "Physics", "status": "Active"}, format='json')
        response = create_course(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddStudentInCourseTestCase(unittest.TestCase):
    @patch('RateRatePro.views.StudentCourses')
    @patch('RateRatePro.views.StudentCourseSerializer')
    def test_add_student_in_course(self, mock_serializer, mock_student_courses):
        mock_student_courses.objects.filter.return_value.exists.return_value = False

        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.save.return_value = MagicMock()
        mock_serializer.return_value = mock_serializer_instance

        request = factory.post('/v1/course/add_student/', {"student_id": 1, "course_id": 1}, format='json')
        response = add_student_in_course(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CreateDepartmentTestCase(unittest.TestCase):
    @patch('RateRatePro.views.DepartmentSerializer')
    def test_create_department(self, mock_serializer):
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.save.return_value = MagicMock(id=1, name="Physics")
        mock_serializer.return_value = mock_serializer_instance

        request = factory.post('/v1/department/create/', {"name": "Physics"}, format='json')
        response = create_department(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PostRatingTestCase(unittest.TestCase):
    @patch('RateRatePro.views.RatingsSerializer')
    @patch('RateRatePro.views.StudentCourses')
    def test_post_rating(self, mock_student_courses, mock_serializer):
        mock_student_courses.objects.filter.return_value.exists.return_value = True

        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.save.return_value = MagicMock()
        mock_serializer.return_value = mock_serializer_instance

        request = factory.post('/v1/rating/post/', {
            "course_id": 1,
            "student_id": 1,
            "professor_id": 1,
            "feedback": "Great course!"
        }, format='json')
        response = post_rating(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FetchOverallRatingTestCase(unittest.TestCase):
    @patch('RateRatePro.views.Ratings')
    def test_fetch_overall_rating(self, mock_ratings):
        mock_ratings.objects.filter.return_value.exists.return_value = True
        mock_ratings.objects.filter.return_value.aggregate.return_value = {
            'overall_rating_avg': 4.5,
            'would_take_again_count_1': 10,
            'would_take_again_count_0': 5,
            'academic_ability_avg': 4.2,
            'teaching_ability_avg': 4.3,
            'interactions_with_students_avg': 4.0,
            'hardness_avg': 3.5
        }

        request = factory.get('/v1/rating/overall/', {"professor_id": 1})
        response = fetch_overall_rating(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
