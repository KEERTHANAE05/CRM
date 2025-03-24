from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Customer
from django.core.mail import send_mail
from .models import Activity
from django.shortcuts import render
from django.utils.timezone import now
from datetime import datetime 
from django.views.decorators.csrf import csrf_exempt

def crm_dashboard(request):
    raw_statuses = ["new", "Follow_up_1", "Follow_up_2", "Follow_up_3", "not_interested"]
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

