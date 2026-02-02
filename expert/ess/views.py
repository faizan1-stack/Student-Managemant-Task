from .serializer import *
from .utils import *
from .models import *
from .premission import IsVerifiedTeacher
from ess.tasks import send_ess_otp
from Teacher.tasks import discard_expired_enrollments, send_pending_reminders
from django.http import JsonResponse

from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import AuthenticationFailed

user = get_user_model()
def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class StudentRegistor(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            student = serializer.save(is_active=False)
            user = student.user

            otp_obj = OTP.objects.create(user=user)
            otp_obj.generate_otp()
            send_ess_otp.delay(user.email, otp_obj.otp_code)

            return Response(
                success_response(
                    data=serializer.data,
                    message="Student Registred successfully , please verified your email"
                ),
                status=status.HTTP_201_CREATED
            )
        return Response(
            error_response(message="Invalid data"),
            status=status.HTTP_400_BAD_REQUEST
        )

class VerifyOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.get(user=user)
        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response(
                error_response(message="Invalid email or OTP"),
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp.is_expired():
            otp.delete()
            return Response(
                error_response(message="OTP expired. Please request a new one."),
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp.otp_code == otp_code:
            otp.delete()
            user.is_active = True
            user.save()
            return Response(
                success_response(message="OTP verified successfully"),
                status=status.HTTP_200_OK
            )
        return Response(
            error_response(message="Invalid OTP"),
            status=status.HTTP_400_BAD_REQUEST
        )

class StudentLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.validated_data['user']

                if not user.is_active:
                    return Response(
                        error_response(message="Account is not verified. Please verify your email."),
                        status=status.HTTP_403_FORBIDDEN
                    )
                token = get_tokens_for_user(user)
                return Response(
                    success_response(
                        data={
                            'token': token,
                            'user_id': user.id,
                            'username': user.username
                        },
                        message="Login successful"
                    ),
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                error_response(message=str(e)),
                status=status.HTTP_400_BAD_REQUEST
            )

class StudentView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response(
                error_response(message="Student not found"),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StudentSerializer(student, data=request.data, partial=False)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                success_response(
                    data=serializer.data,
                    message="Student updated successfully"
                ),
                status=status.HTTP_200_OK
            )

    def patch(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response(
                error_response(message="Student not found"),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                success_response(
                    data=serializer.data,
                    message="Student updated successfully"
                ),
                status=status.HTTP_200_OK
            )

    def get(self, request, pk=None):
        if pk:
            try:
                student = Student.objects.get(pk=pk)
            except Student.DoesNotExist:
                return Response(
                    error_response(message="Student not found"),
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = StudentSerializer(student)
            return Response(
                success_response(data=serializer.data),
                status=status.HTTP_200_OK
            )

        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(
            success_response(data={"students": serializer.data}),
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response(
                error_response(message="Student not found"),
                status=status.HTTP_404_NOT_FOUND
            )

        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



