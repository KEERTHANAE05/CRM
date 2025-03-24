from django.db import models
from datetime import date 

class Customer(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("Follow_up_1", "Follow Up 1"),
        ("Follow_up_2", "Follow Up 2"),
        ("Follow_up_3", "Follow Up 3"),
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
    opportunity = models.CharField(max_length=255)
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



