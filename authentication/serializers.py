import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from authentication.models import User
from base.constants import UserType
from base.validators import ProfilePictureValidator


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'first_name', 'last_name', 
                 'middle_name', 'phone_number', 'profile_picture']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        return value.lower()
    
    def validate_phone_number(self, value):
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        return value
    
    def validate_profile_picture(self, value):
        try:
            ProfilePictureValidator.validate_all(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if len(attrs['password']) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
            
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            middle_name=validated_data.get('middle_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            profile_picture=validated_data.get('profile_picture',None)
        )
        return user
    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")
            
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        
        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")
            
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
            
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 
                 'middle_name', 'phone_number', 'profile_picture']
        read_only_fields = ['id', 'email']
    
    def validate_phone_number(self, value):
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        return value
    def validate_profile_picture(self, value):
        try:
            ProfilePictureValidator.validate_all(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value
    

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'phone_number', 'profile_picture']
    
    def validate_phone_number(self, value):
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        return value
    
    def validate_profile_picture(self, value):
        try:
            ProfilePictureValidator.validate_all(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "New passwords don't match."})
        
        if len(attrs['new_password']) < 8:
            raise serializers.ValidationError({"new_password": "Password must be at least 8 characters long."})
            
        return attrs