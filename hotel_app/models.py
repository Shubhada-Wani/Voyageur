from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import random
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone


# ==========================
# DESTINATION
# ==========================

class Destination(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="destinations/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ==========================
# HOTEL
# ==========================

class Hotel(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name="hotels")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="hotels/", blank=True, null=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ==========================
# BOOKING
# ==========================

class Booking(models.Model):
    PAYMENT_CHOICES = [
        ("Pay at Hotel", "Pay at Hotel"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField()
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"


# ==========================
# BLOG
# ==========================

class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="blogs/", blank=True, null=True)
    featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ==========================
# REVIEW
# ==========================

class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"


# ==========================
# CONTACT MESSAGE
# ==========================

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)
