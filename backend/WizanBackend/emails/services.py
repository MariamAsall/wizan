from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_welcome_email(user):
    html = render_to_string("emails/welcome.html", {
        "name": user.first_name or user.username,
    })

    send_mail(
        subject="Welcome to Wizan 🎉",
        message="Welcome to Wizan! Your cognitive journey starts today.", 
        from_email=f"Wizan <{settings.DEFAULT_FROM_EMAIL}>", 
        recipient_list=[user.email],
        html_message=html,
)
    
def send_reset_email(user, token, uid):
    reset_link = f"http://localhost:5173/reset-password?token={token}&uid={uid}"
    
    html = render_to_string("emails/reset.html", {
        "name": user.first_name or user.username,
        "reset_link": reset_link,
    })

    send_mail(
        subject="Reset your Wizan password",
        message=f"Click this link to reset your password: {reset_link}",
        from_email=f"Wizan <{settings.DEFAULT_FROM_EMAIL}>",
        recipient_list=[user.email],
        html_message=html,
    )