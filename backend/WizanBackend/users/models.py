from django.db import models

# Create your models here.


from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):

    LANGUAGES = ( ('en', 'English'), ('ar', 'Arabic'),)

    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=255)
    language = models.CharField( max_length=10, choices=LANGUAGES, default='en' )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email