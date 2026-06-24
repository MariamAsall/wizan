import resend
from django.conf import settings
from django.template.loader import render_to_string

resend.api_key = settings.RESEND_API_KEY

def send_welcome_email(user):
    html = render_to_string("emails/welcome.html", {
        "name": user.first_name or user.username,
    })

    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": user.email,
        "subject": "Welcome to Wizan 🎉",
        "html": html,
    })