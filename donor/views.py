from django.shortcuts import render,redirect
from .models import Donor
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import Donation
from django.core.mail import send_mail
from datetime import timedelta, date
from django.utils.dateparse import parse_date



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


def edit_profile(request):
    return render(request,'footer.html')

# book_appointment

def book_appointment(request):
    return render(request,'footer.html')