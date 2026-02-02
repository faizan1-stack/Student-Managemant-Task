from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate



class StudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = Student
        fields = ['id', 'username', 'email', 'phone_number', 'password', 'password2']

    def validate_email(self, value):
        if self.instance is None:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if self.instance is None:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("Username already exists")
        return value

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password or password2:
            if password != password2:
                raise serializers.ValidationError({
                    "password": "Passwords do not match"
                })
            if len(password) < 8 or len(password) > 16:
                raise serializers.ValidationError({
                    "password": "Password must be between 8 and 16 characters"
                })
        return data

    def create(self, validated_data):
        validated_data.pop('password2', None)
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        phone_number = validated_data.pop('phone_number', '')
        password = validated_data.pop('password')
        role = 'student'
        
        user = User.objects.create_user(
            username=username,
            email=email,
            phone_number = phone_number,
            password=password,
            role = role
        )
        student = Student.objects.create(
            user=user,
            username=username,
            email=email,
            phone_number=phone_number
        )
        return student

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password2', None)
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', None)
        phone_number = validated_data.pop('phone_number', None)
  
        
        if password:
            instance.user.set_password(password)
            instance.user.save()
        if username:
            instance.user.username = username
            instance.user.save()
            instance.username = username
        if email:
            instance.user.email = email
            instance.email = email
        if phone_number is not None:
            instance.phone = phone_number
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['username'] = instance.user.username
        return data

class TeacherSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = Teacher
        fields = ['id', 'username',  'email', 'phone_number', 'department', 'password', 'password2']

    def validate_email(self, value):
        if self.instance is None:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_username(self, value):
        if self.instance is None:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("Username already exists")
        return value

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        
        if password or password2:
            if password != password2:
                raise serializers.ValidationError({
                    "password": "Passwords do not match"
                })
            if len(password) < 8 or len(password) > 16:
                raise serializers.ValidationError({
                    "password": "Password must be between 8 and 16 characters"
                })
        return data

    def create(self, validated_data):
        username = validated_data.pop('username', None)
        email = validated_data.pop('email')
        phone_number = validated_data.pop('phone_number', '')
        password = validated_data.pop('password')
        validated_data.pop('password2', None)
        role = 'teacher'
        department = validated_data.pop('department', None)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            phone_number = phone_number,
            password=password,
            role=role
        )
        teacher = Teacher.objects.create(
            user=user,
            username=username,
            email=email,
            phone_number=phone_number,
            department=department
        )
        return teacher


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'")
        data['user'] = user
        return data    

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'department']

class EnrollmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentRequest
        fields = ['id', 'student', 'course', 'status', 'created_at', 'updated_at']
        read_only_fields = ['status']

class EnrollmentApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentRequest
        fields = ['status'] 

