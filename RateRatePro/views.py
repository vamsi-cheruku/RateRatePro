from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import Users
from .serializers import UserInputSerializer, UserResponseSerializer
import json

@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        serializer = UserInputSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()  # Insert data into User table
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        error_message = list(serializer.errors.values())[0][0]
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def fetch_user(request):
    userid = request.query_params.get('userid')
    
    if userid:
        try:
            user = Users.objects.get(userid=userid)
            serializer = UserResponseSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            # Catch validation errors and format the response
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
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