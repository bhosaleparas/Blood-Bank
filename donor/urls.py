from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
   path('', views.index, name='index'),
   path('register/', views.register_donor, name='register_donor'),
   path('login_donor/', views.login_donor, name='login_donor'),
   path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
   path('logout/',views.logout,name='logout'),
   path('edit_profile/',views.edit_profile,name='edit_profile'),
   # path('book_appointment/',views.book_appointment,name='book_appointment'),
   path('record_donation/',views.record_donation,name='record_donation'),
   
   path('register_receiver/',views.register_receiver,name='register_receiver'),
   path('login_receiver/',views.login_receiver,name='login_receiver'),
   path('receiver_dashboard/',views.receiver_dashboard,name='receiver_dashboard'),
   path('receiver_logout/',views.receiver_logout,name='receiver_logout'),
   path('make_blood_request/', views.make_blood_request, name='make_blood_request'),
   path('cancel-request/<int:request_id>/', views.cancel_request, name='cancel_request'),
   path('search-blood/', views.search_blood, name='search_blood'),




   
   
    path('paras/',views.paras,name='paras'),
   

   

   
   

]