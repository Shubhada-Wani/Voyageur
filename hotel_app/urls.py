from django.urls import path
from . import views

urlpatterns = [

    # ==========================
    # HOME
    # ==========================
    path('', views.home, name='home'),

    # ==========================
    # HOTELS
    # ==========================
    path('search/', views.search_hotels, name='search_hotels'),
    # HOTELS
    path('hotel/<slug:slug>/', views.hotel_detail, name='hotel_detail'),
    path('hotel/<slug:slug>/book/', views.book_hotel, name='book_hotel'),
    path('hotel/<slug:slug>/review/', views.add_review, name='add_review'),
    path('hotels/', views.hotel_list, name='hotels'),


    # ==========================
    # BOOKINGS
    # ==========================
    path('booking/confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),


    # ==========================
    # BLOGS
    # ==========================
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),


    # ==========================
    # CONTACT
    # ==========================
    path('contact/', views.contact, name='contact'),

    # ==========================
    # AUTH
    # ==========================
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('otp-verify/<int:user_id>/', views.otp_verify, name='otp_verify'),
    path('resend_otp/<int:user_id>/', views.resend_otp, name='resend_otp'),

]
