from django.db import models
from datetime import date 

class Customer(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("Stage_1", "Stage 1"),
        ("Stage_2", "Stage 2"),
        ("Stage_3", "Stage 3"),
        ("not_interested", "Not Interested"),
    ]
    
    ACTIVITY_CHOICES = [
        ("", "No Activity"),
        ("call", "Call"),
        ("email", "Email"),
        ("whatsapp", "Whatsapp"),
    ]

    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=20)
    email = models.EmailField()
    company_name = models.CharField(max_length=255)
    date = models.DateField(default=date.today) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, blank=True)
 

class Activity(models.Model):
    ACTIVITY_CHOICES = [
        ("call", "Call"),
        ("email", "Email"),
        ("whatsapp", "WhatsApp"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="activities")
    type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    date = models.DateField()
    summary = models.TextField(blank=True, null=True) 
    

    def __str__(self):
        return f"{self.type} - {self.customer.name}"


from django.db import models


class CustomerConfirmation(models.Model):
    STATUS_CHOICES = [
        ('advertisement_confirm', 'Advertisement Confirm'),
        ('not_interested', 'Not Interested'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company_name} - {self.get_status_display()}"
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    database_name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.database_name}"