from django.core.mail import send_mail  
from django.conf import settings
from celery import shared_task

def success_response(data=None, message="Success", status_code=200):
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(message="Error", errors=None):
    return {
        "success": False,
        "message": message,
        "errors": errors
    }


@shared_task(bind=True, max_retries=3)
def send_otp_email(self , email, otp):
    send_mail(
        subject="Verify your account",
        message=f"Your OTP code is {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )
