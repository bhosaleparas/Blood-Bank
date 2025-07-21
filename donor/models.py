from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Create your models here.

class Donor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    # blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    blood_group=models.CharField(max_length=3)
    date_of_birth = models.DateField()
    # last_donation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    password=models.CharField(max_length=128)
    donor_indentity=models.CharField(max_length=15,unique=True)

    def __str__(self):
        return f"{self.name} ({self.blood_group})"



class Donation(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    donation_id = models.CharField(max_length=20)
    amount_donated = models.PositiveIntegerField(
        validators=[MinValueValidator(300), MaxValueValidator(500)],
        help_text="Amount in milliliters (300-500ml)"
    )
    blood_type = models.CharField(max_length=3)
    hospital_name = models.CharField(max_length=100)
    donation_date = models.DateField()
    city=models.CharField(max_length=100)
    # is_verified = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-donation_date']
        verbose_name = "Blood Donation"
        verbose_name_plural = "Blood Donations"
    
    def __str__(self):
        return f"Donation #{self.donation_id} by {self.donor.user.get_full_name()}"
    
    
class BloodStock(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    blood_type = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Quantity in milliliters")
    hospital_name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.blood_type} - {self.quantity}ml at {self.hospital_name} ({self.city})"
    
    
# Create your models here.

class Receiver(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    # blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    blood_group=models.CharField(max_length=3)
    date_of_birth = models.DateField()
    # last_donation_date = models.DateField(null=True, blank=True)
    password=models.CharField(max_length=128)
    def __str__(self):
        return f"{self.name} ({self.blood_group})"



class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('FULFILLED', 'Fulfilled'),
    ]
    
    requester = models.ForeignKey(Receiver, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BloodStock.BLOOD_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    reason = models.TextField()
    hospital = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)