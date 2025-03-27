from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path("index", views.crm_dashboard, name="index"),
    path("add_customer/", views.add_customer, name="add_customer"),
    path("save_activity/", views.save_activity, name="save_activity"),
    path("update_status/", views.update_status, name="update_status"),
    path("customer_details/<int:customer_id>/", views.customer_details, name="customer_details"),
    path("send_email/", views.send_email, name="send_email"),
    path("customer_schedule", views.customer_activity_view, name="customer_schedule"),
    path('expired_activities/', views.expired_activity_view, name='expired_activities'), 
    path('save_confirmation/', views.save_confirmation, name='save_confirmation'),
    path('confirmations/', views.confirmation_page, name='confirmation_page'),
    
]