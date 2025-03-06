from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.utils import timezone 
from .country_choices import COUNTRY_CHOICES
# Create your models here.

class CustomUserManager (BaseUserManager):
    def create_user (self, first_name, last_name, email, password=None, user_type='simple_user',**extra_fields):
        if not email:
            raise ValueError('The Email Field must be set.')
        email=self.normalize_email(email)
        user = self.model(
            email=email, 
            first_name=first_name, 
            last_name=last_name, 
            user_type=user_type,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user (first_name, last_name, email, password, **extra_fields)    


class CustomUser (AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('simple_user', 'Simple User'),
        ('illustrator', 'llustrator'),
    ]
    first_name  = models.CharField(max_length=30)
    last_name   = models.CharField(max_length=30)
    email       = models.EmailField(unique=True , primary_key=True)
    biography   = models.TextField(blank=True, null= True)
    country     = models.CharField(max_length=2, choices=COUNTRY_CHOICES[1:], blank=True, null=True)
    state       = models.CharField(max_length=100, blank=True, null=True)
    zip_code    = models.CharField(max_length=20, blank=True, null=True)
    user_type   = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='simple_user')
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name