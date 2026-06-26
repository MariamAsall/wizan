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


def send_score_email(user, score):
    if score >= 60:
        zone = "LOW"
        zone_label = "Great cognitive day 🟢"
        tip = "You're energized today. Wizan has unlocked all your tasks."
    elif score >= 30:
        zone = "MEDIUM"
        zone_label = "Good cognitive day 🟡"
        tip = "You're in solid shape. Wizan arranged your tasks efficiently."
    else:
        zone = "HIGH"
        zone_label = "High cognitive load 🔴"
        tip = "Take it easy today. Wizan reduced your tasks to protect your energy."

    html = render_to_string("emails/score_summary.html", {
        "name": user.first_name or user.username,
        "score": score,
        "zone_label": zone_label,
        "tip": tip,
    })

    send_mail(
        subject=f"Your Wizan score today: {score}/100",
        message=f"Your cognitive score today is {score}/100. {tip}",
        from_email=f"Wizan <{settings.DEFAULT_FROM_EMAIL}>",
        recipient_list=[user.email],
        html_message=html,
    )


def send_deadline_reminder(user, task_name, deadline):
    html = render_to_string("emails/reminder.html", {
        "name": user.first_name or user.username,
        "task_name": task_name,
        "deadline": deadline,
    })

    send_mail(
        subject=f"⏰ Reminder: '{task_name}' is due tomorrow",
        message=f"Hi {user.first_name}, your task '{task_name}' is due tomorrow ({deadline}).",
        from_email=f"Wizan <{settings.DEFAULT_FROM_EMAIL}>",
        recipient_list=[user.email],
        html_message=html,
    )