from rest_framework import serializers
from .models import Users

class UserInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        
class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['userid', 'username', 'nickname', 'major', 'email', 'role']  # fields to include
        extra_kwargs = {
            'password': {'write_only': True}  # This ensures password is not included in the response
        }