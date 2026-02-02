from django.urls import path

from .views import *

from Teacher.views import *
from Course.views import *
from Enroll.views import *

urlpatterns = [
   #student registor and login 
   path('registor/', StudentRegistor.as_view(), name='student'),
   path('student/login/' , StudentLogin.as_view(), name='login'),
   path('student/verify-otp/', VerifyOTP.as_view(), name='verify-otp'),

   #student Url
   path('student/update/<int:pk>/', StudentView.as_view(), name='update'),
   path('student/partial-update/<int:pk>/', StudentView.as_view(), name='partial-update'),
   path('student/get-stud/', StudentView.as_view(), name='get-all-students'),      
   path('student/get-stud/<int:pk>/', StudentView.as_view(), name='get-student'),
   path('student/delete/<int:pk>/', StudentView.as_view(), name='delete'),

   #teacher registor and login
   path('teacher/registor/', TeacherRegistor.as_view(), name='teacher'),
   path('teacher/login/' , TeacherLogin.as_view(), name='login'),
   path('teacher/verify-otp/', VerifyTeacherOtp.as_view(), name='verify-otp'),
   
   #teacher Url
   path('teacher/', TeacherView.as_view(), name='teacher'),
   path('teacher/<int:pk>/', TeacherView.as_view(), name='teacher'),
   path('teacher/update/<int:pk>/', TeacherView.as_view(), name='teacher-update'),
   path('tacher/partial-update/<int:pk>/', TeacherView.as_view(), name='teacher-partial-update'),
   path('teacher/get/', TeacherView.as_view(), name='teacher-get-all'),
   path('teacher/delete/<int:pk>/', TeacherView.as_view(), name='teacher-delete'),

   #course Url
    path('course/', CourseView.as_view(), name='course'),
    path('course/<int:pk>/', CourseView.as_view(), name='course'),
    path('course/update/<int:pk>/', CourseView.as_view(), name='course-update'),
    path('course/partial-update/<int:pk>/', CourseView.as_view(), name='course-partial-update'),
    path('course/get/', CourseView.as_view(), name='course-get-all'),
    path('course/delete/<int:pk>/', CourseView.as_view(), name='course-delete'),

    #Enrollment
    path('enrollment/', EnrollmentRequestView.as_view(), name='enrollment-list-create'),
    path('enrollment/<int:pk>/', EnrollmentRequestView.as_view(), name='enrollment-update'),
   

]
