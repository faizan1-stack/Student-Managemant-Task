from ess.serializer import *
from ess.utils import *
from ess.models import *
from ess.premission import IsVerifiedTeacher

from django.contrib.auth import get_user_model
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied


# Create your views here.
class CourseView(APIView):
    permission_classes = [IsVerifiedTeacher]

    def post(self, request):
        if not request.user.is_active:
            raise PermissionDenied("You are not allowed to create a course")
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            course = serializer.save()
            teacher = Teacher.objects.get(user=request.user)
            course.teacher.add(teacher)
            return Response(
                success_response(
                    data=CourseSerializer(course).data,
                    message="Course created and assigned to teacher"
                ),
                status=status.HTTP_201_CREATED
            )
        return Response(
            error_response(message="Invalid data"),
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied("You are not allowed to update a course")

        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response(
                error_response(message="Course not found"),
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                success_response(
                    data=serializer.data, 
                    message="Course updated successfully"
                ),
                status=status.HTTP_200_OK
            )
        return Response(
            error_response(message="Invalid data"),
            status=status.HTTP_400_BAD_REQUEST
        )


    def patch(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied("You are not allowed to update a course")
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response(
                error_response(message="Course not found"),
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                success_response(
                    data=serializer.data,
                    message="Course updated successfully"
                ),
                status=status.HTTP_200_OK
            )
        return Response(
            error_response(message="Invalid data"),
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request, pk=None):
        if pk:
            try:
                course = Course.objects.get(pk=pk)
            except Course.DoesNotExist:
                return Response(
                    error_response(message="Course not found"),
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = CourseSerializer(course)
            return Response(
                success_response(
                    data=serializer.data,
                    message="Course retrieved successfully"
                ),
                status=status.HTTP_200_OK
            )

        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(
            success_response(
                data=serializer.data,
                message="Courses retrieved successfully"
            ),
            status=status.HTTP_200_OK
        )


    def delete(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied("You are not allowed to delete a course")
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response(
                error_response(message="Course not found"),
                status=status.HTTP_404_NOT_FOUND
            )

        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 



