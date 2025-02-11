from django.db import models
from django.contrib.auth.models import User
from .category import Categories
from django.conf import settings

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    @classmethod
    def initialize_categories(cls):
        # Method to create categories if they don't exist
        for category_name in Categories:
            cls.objects.get_or_create(name=category_name)

    
class Illustration(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category ,on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='illustrations/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mains_illustrations'
    )

    def __str__(self):
        return self.title