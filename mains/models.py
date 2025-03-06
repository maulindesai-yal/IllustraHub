from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.timezone import now

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
SELLING_TYPE_CHOICES = [
    ('sell', 'Fixed Price'),
    ('bid', 'Live Bidding'),
]
    
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
    selling_type = models.CharField(max_length=10, choices=SELLING_TYPE_CHOICES, default='sell')
    bidding_end_time = models.DateTimeField(null=True, blank=True)  # When bidding ends

    def __str__(self):
        return self.title
    
class Bid(models.Model):
    illustration = models.ForeignKey(Illustration, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount']  # Highest bid first

    def __str__(self):
        return f"{self.user.username} - ${self.amount} on {self.illustration.title}"
    
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    illustration = models.ForeignKey('Illustration', on_delete = models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user' , 'illustration')

    def get_total_price(self):
        return self.illustration.price * self.quantity