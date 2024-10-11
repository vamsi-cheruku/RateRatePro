from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    
    #! API endpoints for managing users
    path('v1/user/create/', views.create_user, name='create_user'), # For inserting users
    # path('v1/user/professor/create', views.create_professor, name='create_professor'), # For
    path('v1/user/fetch/', views.fetch_user, name='fetch_user'), # For fetching user details
    path('v1/user/login/', views.authenticate_user, name='authenticate_user'), # For authenticating users using username and password
    
    #! API endpoints for search
    path('v1/user/search/', views.search_users, name='search_users'), # For searching users based on a search query
    
    #! API endpoints for ratings
    path('v1/rating/post/', views.post_rating, name='post_rating'), # For posting a rating for a professor
    path('v1/rating/fetch/', views.get_professor_ratings, name='get_rating'), # For updating a rating for a professor
    
    #! API endpoints for managing courses
    path('v1/course/create', views.create_course, name='create_course'), # For creating a new course
    path('v1/course/addstudent/', views.add_student_in_course, name='add_student_in_course'), # For adding a new student in a course
    
    #! API endpoints for managing professors
    
    #! API endpoints for managing departments
    path('v1/department/create', views.create_department, name='create_department') # For creating a new department
]
