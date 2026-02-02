from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, name='ess.send_otp')
def send_ess_otp(self, email, otp):
    """Send OTP email for ESS app"""
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
        return f"ESS OTP sent to {email}"
    except Exception as exc:
        print(f"Error sending email: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)