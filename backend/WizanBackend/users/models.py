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

    language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.ENGLISH
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email