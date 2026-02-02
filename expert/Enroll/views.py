from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ess.models import EnrollmentRequest, Student, Course
from ess.serializer import EnrollmentRequestSerializer
from rest_framework.exceptions import PermissionDenied

class EnrollmentRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
  
        if not hasattr(request.user, 'student'):
            raise PermissionDenied("Only students can request enrollment.")

        student = request.user.student
        course_id = request.data.get('course')

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        if EnrollmentRequest.objects.filter(student=student, course=course).exists():
            return Response({"error": "You have already requested this course"}, status=status.HTTP_400_BAD_REQUEST)

        enrollment = EnrollmentRequest.objects.create(student=student, course=course)
        serializer = EnrollmentRequestSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
       
        if hasattr(request.user, 'student'):
            enrollments = EnrollmentRequest.objects.filter(student=request.user.student)
        elif hasattr(request.user, 'teacher'):
            teacher = request.user.teacher
            enrollments = EnrollmentRequest.objects.filter(course__teacher=teacher)
        else:
            enrollments = EnrollmentRequest.objects.none()

        serializer = EnrollmentRequestSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    def patch(self, request, pk):
      
        if not hasattr(request.user, 'teacher'):
            raise PermissionDenied("Only teachers can approve/reject requests.")

        try:
            enrollment = EnrollmentRequest.objects.get(pk=pk)
        except EnrollmentRequest.DoesNotExist:
            return Response({"error": "Enrollment request not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user.teacher not in enrollment.course.teacher.all():
            raise PermissionDenied("You are not assigned to this course.")

        status_value = request.data.get('status')
        if status_value not in ["approved", "rejected"]:
            return Response({"error": "Status must be 'approved' or 'rejected'"}, status=status.HTTP_400_BAD_REQUEST)

        enrollment.status = status_value
        enrollment.save()

        if status_value == "approved":
            enrollment.course.student.add(enrollment.student)

        serializer = EnrollmentRequestSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_200_OK)










