from django.shortcuts import render,redirect
from .models import Donor
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import Donation,BloodStock,Receiver,BloodRequest,Admin
from django.core.mail import send_mail
from datetime import timedelta, date
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Max
from django.conf import settings






# Create your views here.



def index(request):
   return render(request, 'index.html')



def register_donor(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        blood_group = request.POST['blood_group']
        dob = request.POST['date_of_birth']
        password = make_password(request.POST['password'])
        city=request.POST['city']
        donor_indentity=request.POST['donor_indentity']

        Donor.objects.create(
            name=name,
            email=email,
            phone=phone,
            blood_group=blood_group,
            date_of_birth=dob,
            password=password,
            address=city,
            donor_indentity=donor_indentity,
        )
        # msg="You registered successfully!"
        messages.success(request, "You registered successfully! You can Login.")
        return redirect('index')

    return render(request, 'register.html')
 
 
 
 
# def login(request):
#    return render(request, 'index.html')


def login_donor(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            donor = Donor.objects.get(email=email)

            if check_password(password, donor.password):
                request.session['donor_id'] = donor.id  
                send_mail(
                    subject='Login Alert - LifeBlood Donor System',
                    message=f"Hi {donor.name}, you have successfully logged in.",
                    from_email=None,  
                    recipient_list=[donor.email],
                    fail_silently=False,
                )
                messages.success(request, "Login successful!")
                return redirect('donor_dashboard')  # Redirect to donor dashboard
            else:
                messages.error(request, "Invalid email or password")
                return redirect('login_donor')

        except Donor.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect('login_donor')

    return render(request, 'index.html')




def donor_dashboard(request):
    donor_id = request.session.get('donor_id')

    if not donor_id:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('register_donor')

    try:
        donor = Donor.objects.get(id=donor_id)
        donations = donor.donations.all().order_by('-donation_date')  
        #  latest donation 
        last_donation_date = donations.first().donation_date if donations.exists() else None
        
        if last_donation_date:
            next_eligible_date = last_donation_date + timedelta(days=60)
            is_eligible = date.today() >= next_eligible_date
        else:
            next_eligible_date = None
            is_eligible = True
            
    except Donor.DoesNotExist:
        messages.error(request, "Invalid session. Please log in again.")
        return redirect('logout')

    return render(request, 'donor_dashboard.html', {
        'donor': donor,
        'donations': donations,
        'last_donation_date': last_donation_date,
        'next_eligible_date': next_eligible_date,
        'is_eligible': is_eligible,

    })




def record_donation(request):
    if request.method == 'POST':
        donation_id = request.POST.get('donation_id')
        logged_in_donor_id = request.session.get('donor_id')

        try:
            donor = Donor.objects.get(donor_indentity=donation_id)
        except Donor.DoesNotExist:
            messages.error(request, "Invalid Donation ID. You are not a registered donor.")
            return redirect('index')  
        
        
        try:
            donor = Donor.objects.get(id=logged_in_donor_id)
            if donor.donor_indentity != donation_id:
                messages.warning(request, "You can only submit a donation using your own Donation ID.")
                return redirect('donor_dashboard')

        except Donor.DoesNotExist:
            messages.error(request, "Invalid session. Please log in again.")
            return redirect('donor_dashboard')
        
        donations = donor.donations.all().order_by('-donation_date') 
        #  latest donation date 
        last_donation_date = donations.first().donation_date if donations.exists() else None
        form_donation_date_str=request.POST.get('donation_date')
        
        form_donation_date = parse_date(form_donation_date_str)

        
        if last_donation_date and form_donation_date < (last_donation_date + timedelta(days=60)):
            messages.error(request, f"Not eligible to donate yet. You can donate after {(last_donation_date + timedelta(days=60)).strftime('%b %d, %Y')}.")
            return redirect('donor_dashboard')

        try:
            donor = Donor.objects.get(id=request.session.get('donor_id')) 
            Donation.objects.create(
                donor=donor,
                donation_id=donation_id, 
                amount_donated=request.POST.get('blood_amount'),
                blood_type=request.POST.get('blood_type'),
                hospital_name=request.POST.get('hospital'),
                donation_date=form_donation_date,
                city=request.POST.get('city'),
            )
            
            amount_donated = int(request.POST.get('blood_amount'))
            blood_type = request.POST.get('blood_type') 
            hospital_name = request.POST.get('hospital')
            city = request.POST.get('city')
            donation_date=form_donation_date
            
            stock, created = BloodStock.objects.get_or_create(
                blood_type=blood_type,
                hospital_name=hospital_name,
                city=city,
                defaults={'quantity': amount_donated}
            )

            if not created:
                stock.quantity += amount_donated
                stock.save()
            
            
            send_mail(
                    subject='Blood donation',
                    message=f"Hi {donor.name}, you have donated {amount_donated}ml, blood type {blood_type} in {hospital_name} hopital {city} at {donation_date}",
                    from_email=None,  
                    recipient_list=[donor.email],
                    fail_silently=False,
                )
            

            messages.success(request, "Thank you for your donation!")
            return redirect('donor_dashboard')  

        except Exception as e:
            messages.error(request, f"Error saving donation: {str(e)}")
            return redirect('donor_dashboard')

    return render(request, 'footer.html')


def logout(request):
    donor_id = request.session.get('donor_id')
    
    if donor_id:
        try:
            donor = Donor.objects.get(id=donor_id)

            send_mail(
                subject='Logout Alert - LifeBlood Donor System',
                message=f"Hi {donor.name}, you have successfully logged out.",
                from_email=None,
                recipient_list=[donor.email],
                fail_silently=False,
            )
        except Donor.DoesNotExist:
            pass

    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')






# ####### Receier code starts from here



def register_receiver(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        blood_group = request.POST['blood_group']
        dob = request.POST['date_of_birth']
        password = make_password(request.POST['password'])
        city=request.POST['city']

        Receiver.objects.create(
            name=name,
            email=email,
            phone=phone,
            blood_group=blood_group,
            date_of_birth=dob,
            password=password,
            address=city,
        )
        # msg="You registered successfully!"
        messages.success(request, "You registered successfully! You can Login.")
        return redirect('index')

    print("paras")
    return render(request, 'register_receiver.html')
 
 
 
 
def login_receiver(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            receiver = Receiver.objects.get(email=email)

            if check_password(password, receiver.password):
                request.session['receiver_id'] = receiver.id  
                send_mail(
                    subject='Login Alert - LifeBlood Donor System',
                    message=f"Hi {receiver.name}, you have successfully logged in.",
                    from_email=None,  
                    recipient_list=[receiver.email],
                    fail_silently=False,
                )
                messages.success(request, "Login successful!")
                return redirect('receiver_dashboard')  # Redirect to donor dashboard
            else:
                messages.error(request, "Invalid email or password")
                return redirect('login_receiver')

        except Receiver.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect('login_receiver')

    return redirect(request,'index.html')



# def receiver_dashboard(request):
#     return render(request,'receiver_dashboard.html')

# @login_required
def receiver_dashboard(request):
    blood_stocks = None
    search_performed = False

    blood_groups = BloodStock.BLOOD_TYPE_CHOICES
    receiver_id = request.session.get('receiver_id')

    blood_requests = []
    blood_stocks=[]

    if receiver_id:
        try:
            receiver = Receiver.objects.get(id=receiver_id)
            
            # Fetch all blood requests made by this receiver
            blood_requests = BloodRequest.objects.filter(requester=receiver).order_by('-created_at')
            name=receiver.name
        
        except Receiver.DoesNotExist:
            pass

    return render(request, 'receiver_dashboard.html', {
        'blood_groups': blood_groups,
        'blood_requests': blood_requests,
        'name':name,
        'blood_stock':blood_stocks,
    })




def receiver_logout(request):
    receiver_id = request.session.get('receiver_id')
    
    if receiver_id:
        try:
            receiver = Receiver.objects.get(id=receiver_id)

            send_mail(
                subject='Logout Alert - LifeBlood Donor System',
                message=f"Hi {receiver.name}, you have successfully logged out.",
                from_email=None,
                recipient_list=[receiver.email],
                fail_silently=False,
            )
        except receiver.DoesNotExist:
            pass

    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')



def make_blood_request(request):
    if request.method == 'POST':
        try:
            receiver_id = request.session.get('receiver_id') 
            if not receiver_id:
                messages.error(request, "You must be logged in to make a blood request.")
                return redirect('receiver_login')  
            receiver = Receiver.objects.get(id=receiver_id)

            BloodRequest.objects.create(
                requester=receiver,
                blood_group=request.POST.get('blood_group'),
                quantity=request.POST.get('quantity'),
                reason=request.POST.get('reason'),
                hospital=request.POST.get('hospital'),
                city=request.POST.get('city'),
            )
            messages.success(request, "Blood request submitted successfully!")
        except Receiver.DoesNotExist:
            messages.error(request, "Invalid receiver.")
        except Exception as e:
            messages.error(request, f"Error creating request: {str(e)}")

    return redirect('receiver_dashboard')


def cancel_request(request, request_id):
    if request.method == 'POST':
        blood_request = get_object_or_404(BloodRequest, id=request_id)

        # Check if user is owner
        receiver_id = request.session.get('receiver_id')
        if blood_request.requester.id != receiver_id:
            messages.error(request, "You are not authorized to cancel this request.")
            return redirect('receiver_dashboard')

        if blood_request.status == 'PENDING':
            blood_request.status = 'Cancelled'
            blood_request.save()
            messages.success(request, "Your request has been cancelled.")
        else:
            messages.warning(request, "Only pending requests can be cancelled.")
    
    return redirect('receiver_dashboard')



def search_blood(request):
    blood_groups = BloodStock.BLOOD_TYPE_CHOICES  # For dropdown reuse
    blood_stocks = []

    if request.method == 'GET':
        blood_group = request.GET.get('blood_group')
        city = request.GET.get('city')
        hospital = request.GET.get('hospital')

        if not blood_group and not city and not hospital:
            messages.warning(request, "Please enter at least one search criterion.")
            return redirect('receiver_dashboard')

        # Start filtering
        blood_stocks = BloodStock.objects.all()

        if blood_group:
            blood_stocks = blood_stocks.filter(blood_type=blood_group)

        if city:
            blood_stocks = blood_stocks.filter(city__icontains=city)

        if hospital:
            blood_stocks = blood_stocks.filter(hospital_name__icontains=hospital)

        if not blood_stocks.exists():
            messages.info(request, "No matching blood stock found.")

    return render(request, 'blood_search.html',  {
        'blood_stocks': blood_stocks,
        'blood_groups': blood_groups,
    })
    
    

# admin starts
def register_admin(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = make_password(request.POST['password'])
        city=request.POST['city']

        Admin.objects.create(
            name=name,
            email=email,
            phone=phone,            
            password=password,
            address=city,
        )
        # msg="You registered successfully!"
        messages.success(request, "You registered successfully! You can Login.")
        return redirect('index')
    return render(request,'register_admin.html')





def login_admin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            admin = Admin.objects.get(email=email)

            if check_password(password, admin.password):
                request.session['admin_id'] = admin.id  
                # send_mail(
                #     subject='Login Alert - LifeBlood Donor System',
                #     message=f"Hi {admin.name}, you have successfully logged in.",
                #     from_email=None,  
                #     recipient_list=[admin.email],
                #     fail_silently=False,
                # )
                messages.success(request, "Login successful!")
                return redirect('admin_dashboard') 
            else:
                messages.error(request, "Invalid email or password")
                return redirect('login_admin')

        except Receiver.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect('login_admin')

    return redirect(request,'index.html')
        
    



def admin_dashboard(request):
    admin_id = request.session.get('admin_id')
    admin = Admin.objects.get(id=admin_id)
    # Get all donors
    # donors = Donor.objects.all()
    donors = Donor.objects.annotate(
    last_donation_date=Max('donations__donation_date')
    ).order_by('-last_donation_date')
    
    receivers = Receiver.objects.all()
    
    blood_stocks = BloodStock.objects.all()
    
    donations = Donation.objects.all()
    
    receiver_requests = BloodRequest.objects.all()
    name=admin.name
    
    context = {
        'donors': donors,
        'receivers': receivers,
        'blood_stocks': blood_stocks,
        'donations': donations,
        'receiver_requests': receiver_requests,
        'name':name,
    }
    return render(request, 'admin_dashboard.html', context)


def approve_request(request, request_id):
    if request.method == 'POST':
        blood_request = get_object_or_404(BloodRequest, id=request_id)
        
        # Check if request is already processed
        if blood_request.status != 'PENDING':
            messages.warning(request, 'This request has already been processed.')
            return redirect('admin_dashboard')
        
        # Check blood stock availability
        try:
            blood_stock = BloodStock.objects.get(
                blood_type=blood_request.blood_group,
                hospital_name=blood_request.hospital
            )
            
            if blood_stock.quantity >= blood_request.quantity:
                # Reduce the blood stock
                blood_stock.quantity -= blood_request.quantity
                blood_stock.save()
                
                # Update request status
                blood_request.status = 'APPROVED'
                blood_request.save()
                
                # Send approval email
                # send_request_status_email(blood_request, is_approved=True)
                
                messages.success(request, 'Request approved successfully. Blood stock updated.')
            else:
                messages.error(request, 'Insufficient blood stock to fulfill this request.')
        
        except BloodStock.DoesNotExist:
            messages.error(request, 'No blood stock found for this blood type at the specified hospital.')
        
        return redirect('admin_dashboard')

def reject_request(request, request_id):
    if request.method == 'POST':
        blood_request = get_object_or_404(BloodRequest, id=request_id)
        
        # Check if request is already processed
        if blood_request.status != 'PENDING':
            messages.warning(request, 'This request has already been processed.')
            return redirect('admin_dashboard')
        
        # Update request status
        blood_request.status = 'REJECTED'
        blood_request.save()
        
        # Send rejection email
        # send_request_status_email(blood_request, is_approved=False)
        
        messages.success(request, 'Request has been rejected.')
        return redirect('admin_dashboard')

def send_request_status_email(blood_request, is_approved):
    subject = "Your Blood Request Status Update"
    recipient = blood_request.requester.email
    
    context = {
        'receiver_name': blood_request.requester.name,
        'blood_group': blood_request.blood_group,
        'quantity': blood_request.quantity,
        'hospital': blood_request.hospital,
        'is_approved': is_approved,
        'reason': blood_request.reason if not is_approved else None,
    }
    
    # Render HTML email template
    html_message = render_to_string('request_status_update.html', context)
    plain_message = render_to_string('request_status_update.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        html_message=html_message,
    )
    
    
    
def logout_admin(request):
    admin_id = request.session.get('admin_id')
    
    if admin_id:
        try:
            admin = Admin.objects.get(id=admin_id)

            send_mail(
                subject='Logout Alert - LifeBlood Donor System',
                message=f"Hi {admin.name}, you have successfully logged out.",
                from_email=None,
                recipient_list=[admin.email],
                fail_silently=False,
            )
        except admin.DoesNotExist:
            pass

    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')


def edit_profile(request):
    return render(request,'footer.html')

# book_appointment

def paras(request):
    return render(request,'footer.html')
