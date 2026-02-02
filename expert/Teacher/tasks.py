from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from ess.models import *

import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='teacher.send_otp')
def send_teacher_otp(self, email, otp):
    """Send OTP email for Teacher app"""
    subject = "Your OTP Code for verification"
    message = f"Your OTP is {otp}"
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return f"Teacher OTP sent to {email}"
    except Exception as exc:
        print(f"Error sending email: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    

@shared_task(bind=True, name='Teacher.tasks.discard_expired_enrollments')
def discard_expired_enrollments(self):
    try:
        expiration = timezone.now() - timedelta(minutes=1)

        expired_qs = EnrollmentRequest.objects.filter(
            created_at__lte=expiration,
            status='pending'
        )

        expired_list = list(expired_qs)

        if not expired_list:
            logger.info("No expired enrollments found; nothing to email.")
            logger.info(f"Mail backend: {settings.EMAIL_BACKEND}, sender: {settings.EMAIL_HOST_USER}")
            return "No expired enrollments"

        courses_to_check = set()
        
        expired_qs.update(status='discarded')

        logger.info(f"Found {len(expired_list)} expired enrollments to discard")
        logger.info(f"Mail backend: {settings.EMAIL_BACKEND}, sender: {settings.EMAIL_HOST_USER}")
      
        for enrollment in expired_list:
            try:
                student = enrollment.student
                student_email = getattr(student, "email", None) or getattr(getattr(student, "user", None), "email", None)
                course = enrollment.course
                course_name = course.name
                student_name = getattr(student, "username", "Student")

                courses_to_check.add(course)

                if not student_email:
                    logger.warning(f"Skip email: missing student email for enrollment {enrollment.id}")
                    continue

                logger.info(f"Sending discard email to {student_email} for {course_name}")
                send_mail(
                    subject=f"Enrollment Request for {course_name} has been discarded",
                    message=f"Dear {student_name},\n\nYour enrollment request for the course {course_name} has been discarded due to inactivity.\n\nBest regards,\nThe Course Team",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[student_email],
                    fail_silently=False,
                )
                logger.info(f"Sent discard email to {student_email}")
            except Exception as e:
                logger.error(f"Failed to send email for enrollment {enrollment.id}: {e}")
                continue

        deleted_courses = 0
        for course in courses_to_check:
            remaining_enrollments = EnrollmentRequest.objects.filter(
                course=course,
                status__in=['pending', 'approved', 'enrolled']
            ).count()
            
            if remaining_enrollments == 0:
                logger.info(f"Deleting course {course.name} - no remaining enrollments")
                course.delete()
                deleted_courses += 1
                
        return f"Discarded {len(expired_list)} enrollments and deleted {deleted_courses} courses"
    except Exception as e:
        logger.error(f"Error in discard task: {e}")
        return f"Error: {e}"

@shared_task(bind=True, name='Teacher.tasks.send_pending_reminders')
def send_pending_reminders(self):
    for teacher in Teacher.objects.all():
        try:
            pending_count = EnrollmentRequest.objects.filter(
                course__teacher=teacher,
                status='pending'
            ).count()
            
            if pending_count > 0:
                recipient_email = getattr(teacher.user, 'email', None) if hasattr(teacher, 'user') else getattr(teacher, 'email', None)
                
                if recipient_email:
                    send_mail(
                        subject=f'{pending_count} pending approvals',
                        message=f'You have {pending_count} enrollments to review.',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[recipient_email],
                        fail_silently=True,
                    )
                    logger.info(f"Sent reminder to {recipient_email}")
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")

