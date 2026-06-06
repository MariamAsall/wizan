from django.db import models

# Create your models here.


from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"

    class Language(models.TextChoices):
        ENGLISH = "en", "English"
        ARABIC = "ar", "Arabic"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT
    )

    email = models.EmailField(unique=True)

    is_approved = models.BooleanField(default=True)

    language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.ENGLISH
    )
    phone_number = models.CharField(max_length=20, blank=True)

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
    )
    date_of_birth = models.DateField(null=True, blank=True)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

def __str__(self) -> str:
        return f"{self.get_full_name()} ({self.role}) — {self.email}"
