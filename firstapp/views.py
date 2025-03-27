from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Customer
from django.core.mail import send_mail
from .models import Activity
from django.shortcuts import render
from django.utils.timezone import now
from datetime import datetime 
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User  # This is the missing import
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('crm_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('crm_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('crm_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        errors = []
        
        if not username or not email or not password1 or not password2:
            errors.append('All fields are required.')
        
        if password1 != password2:
            errors.append('Passwords do not match.')
        
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if not any(char.isdigit() for char in password1):
            errors.append('Password must contain at least one number.')
        
        if not any(char.isupper() for char in password1):
            errors.append('Password must contain at least one uppercase letter.')
        
        if not any(char.islower() for char in password1):
            errors.append('Password must contain at least one lowercase letter.')
        
        if User.objects.filter(username=username).exists():
            errors.append('Username is already taken.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email is already registered.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )
                messages.success(request, 'Registration successful. Please login.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
    
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def crm_dashboard(request):
    raw_statuses = ["new", "Stage_1", "Stage_2", "Stage_3", "not_interested"]
    statuses = {status: status.replace("_", " ").title() for status in raw_statuses}
    customers = Customer.objects.all()

    selected_customer_id = request.GET.get("customer_id")  
    selected_customer = None

    if selected_customer_id:
        selected_customer = get_object_or_404(Customer, id=selected_customer_id)

    for customer in customers:
        customer.status_display = statuses.get(customer.status, customer.status)

    return render(request, "index.html", {
        "statuses": statuses.values(),
        "customers": customers,
        "selected_customer": selected_customer,
    })
    
def add_customer(request):
    if request.method == "POST":
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        opportunity = request.POST.get("opportunity")
        date = request.POST.get("date")  # Get date from request

        if name and contact and email and opportunity and date:
            try:
                # Convert date string to proper format if needed
                date_obj = datetime.strptime(date, "%Y-%m-%d").date()  

                # Save customer including date
                Customer.objects.create(
                    name=name,
                    contact=contact,
                    email=email,
                    opportunity=opportunity,
                    date=date_obj  # Save date to database
                )

                return JsonResponse({"success": True})
            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)})

        return JsonResponse({"success": False, "message": "All fields are required!"})


  # Ensure these models exist

def save_activity(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        activity_date = request.POST.get("activity_date")
        activity_type = request.POST.get("activity")
        summary = request.POST.get("summary")

        if not customer_id or not activity_date or not activity_type or not summary:
            return JsonResponse({"success": False, "message": "All fields are required!"})

        try:
            
            customer = get_object_or_404(Customer, id=customer_id)

            activity = Activity.objects.create(
                customer=customer,
                date=activity_date,
                type=activity_type,
                summary=summary
            )
            customer.activity = activity_type  
            customer.save()

            return JsonResponse({"success": True, "message": "Activity saved successfully!", "activity": activity_type})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method!"})

def update_status(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        new_status = request.POST.get("status")
        
        customer = get_object_or_404(Customer, id=customer_id)
        customer.status = new_status
        customer.save()
        
        return JsonResponse({"success": True, "new_status": new_status})
    return JsonResponse({"success": False, "message": "Invalid request"})

def customer_details(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    return render(request, "customer_details.html", {"customer": customer})

def send_email(request):
    if request.method == "POST":
        to_email = request.POST.get("to_email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if not to_email or not subject or not message:
            return JsonResponse({"success": False, "message": "All fields are required!"})

        try:
            send_mail(
                subject,
                message,
                "keerthikala1105@gmail.com",  # Replace with your email
                [to_email],
                fail_silently=False,
            )
            return JsonResponse({"success": True, "message": "Email sent successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})



def customer_activity_view(request):
    customers = Customer.objects.all()
    customer_activities = {}  
    today = now().date()

    for customer in customers:
        call_activity = Activity.objects.filter(customer=customer, type="call").order_by("-date").first()
        email_activity = Activity.objects.filter(customer=customer, type="email").order_by("-date").first()
        whatsapp_activity = Activity.objects.filter(customer=customer, type="whatsapp").order_by("-date").first()

        call_date = call_activity.date if call_activity else None
        email_date = email_activity.date if email_activity else None
        whatsapp_date = whatsapp_activity.date if whatsapp_activity else None

        valid_call = call_date if call_date and call_date >= today else None
        valid_email = email_date if email_date and email_date >= today else None
        valid_whatsapp = whatsapp_date if whatsapp_date and whatsapp_date >= today else None

        if valid_call or valid_email or valid_whatsapp:
            customer_activities[customer.id] = {
                "customer": customer,
                "call_date": valid_call,
                "email_date": valid_email,
                "whatsapp_date": valid_whatsapp,
            }

    return render(request, "customer_schedule.html", {"customer_activities": customer_activities})

def expired_activity_view(request):
    customers = Customer.objects.all()
    expired_activities = {}  
    today = now().date()

    for customer in customers:
        call_activity = Activity.objects.filter(customer=customer, type="call").order_by("-date").first()
        email_activity = Activity.objects.filter(customer=customer, type="email").order_by("-date").first()
        whatsapp_activity = Activity.objects.filter(customer=customer, type="whatsapp").order_by("-date").first()

        call_date = call_activity.date if call_activity else None
        email_date = email_activity.date if email_activity else None
        whatsapp_date = whatsapp_activity.date if whatsapp_activity else None

        expired_call = call_date if call_date and call_date < today else None
        expired_email = email_date if email_date and email_date < today else None
        expired_whatsapp = whatsapp_date if whatsapp_date and whatsapp_date < today else None

        if expired_call or expired_email or expired_whatsapp:
            expired_activities[customer.id] = {
                "customer": customer,
                "call_date": expired_call,
                "email_date": expired_email,
                "whatsapp_date": expired_whatsapp,
            }

    
    return render(request, "expired_activities.html", {"expired_activities": expired_activities})

from .models import CustomerConfirmation
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Temporary for debugging - remove in production
def save_confirmation(request):
    if request.method == 'POST':
        try:
            # Try to parse JSON if content-type is application/json
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Required fields
            required_fields = ['customer_id', 'company_name', 'status', 'date']
            if not all(field in data for field in required_fields):
                return JsonResponse({
                    'success': False,
                    'message': 'All fields are required'
                }, status=400)

            # Create confirmation (replace with your actual model)
            confirmation = CustomerConfirmation.objects.create(
                customer_id=data['customer_id'],
                company_name=data['company_name'],
                status=data['status'],
                date=data['date']
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Confirmation saved successfully',
                'confirmation_id': confirmation.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e),
                'error': 'Server error occurred'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Only POST requests are allowed'
    }, status=405)
    
    
def confirmation_page(request):
    confirmations = CustomerConfirmation.objects.select_related('customer').order_by('-date')
    return render(request, 'confirmation_page.html', {'confirmations': confirmations})


