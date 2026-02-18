from django.contrib import admin

from django.contrib import admin
from .models import Destination, Hotel, Booking, Blog, Review, ContactMessage


# ==========================
# DESTINATION ADMIN
# ==========================

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


# ==========================
# HOTEL ADMIN
# ==========================

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "destination", "price_per_night", "featured", "created_at")
    list_filter = ("featured", "destination")
    search_fields = ("name", "destination__name")
    prepopulated_fields = {"slug": ("name",)}


# ==========================
# BOOKING ADMIN
# ==========================

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "hotel", "check_in", "check_out", "guests", "payment_method", "created_at")
    list_filter = ("payment_method", "created_at")
    search_fields = ("user__username", "hotel__name")


# ==========================
# BLOG ADMIN
# ==========================

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "featured", "published_at")
    list_filter = ("featured",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


# ==========================
# REVIEW ADMIN
# ==========================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "hotel", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "hotel__name")


# ==========================
# CONTACT MESSAGE ADMIN
# ==========================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")
