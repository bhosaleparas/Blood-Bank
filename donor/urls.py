from django.urls import path
from . import views

urlpatterns = [
   path('', views.index, name='index'),
   path('register/', views.register_donor, name='register_donor'),
   path('login_donor/', views.login_donor, name='login_donor'),
   path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
   path('logout/',views.logout,name='logout'),
   path('edit_profile/',views.edit_profile,name='edit_profile'),
   path('book_appointment/',views.book_appointment,name='book_appointment'),
   path('record_donation/',views.record_donation,name='record_donation'),

   
   

]