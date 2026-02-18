from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.core.mail import send_mail
from .models import Hotel, Destination, Booking, Blog, Review, ContactMessage,EmailOTP
from django.core.mail import EmailMessage
from .utils import generate_booking_pdf
from django.urls import reverse
from django.conf import settings
from .utils import send_otp_email
from django.contrib.auth import login as auth_login



# ==========================
# HOME
# ==========================

def home(request):
    featured_hotels = Hotel.objects.filter(featured=True)[:6]
    featured_blogs = Blog.objects.filter(featured=True)[:3]
    destinations = Destination.objects.all()[:6]

    context = {
        "featured_hotels": featured_hotels,
        "featured_blogs": featured_blogs,
        "destinations": destinations,
    }
    return render(request, "home.html", context)


# ==========================
# SEARCH HOTELS
# ==========================

def search_hotels(request):
    city_slug = request.GET.get('city')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    guests = request.GET.get('guests')

    hotels = Hotel.objects.all()

    if city_slug:
         hotels = hotels.filter(
            destination__name__icontains=city_slug  # ✅ search by name, case-insensitive
        ) | Hotel.objects.filter(
            destination__slug__icontains=city_slug  # ✅ also match slug
        ) | Hotel.objects.filter(
            name__icontains=city_slug              # ✅ also match hotel name itself
        )


    return render(request, 'hotel_list.html', {
        'hotels': hotels,
        'check_in': check_in,
        'check_out': check_out,
        'guests': guests,
    })



def hotel_list(request):
    hotels = Hotel.objects.all()
    return render(request, 'hotels.html', {'hotels': hotels})


# ==========================
# HOTEL DETAIL
# ==========================

def hotel_detail(request, slug):
    hotel = get_object_or_404(Hotel, slug = slug)
    reviews = Review.objects.filter(hotel=hotel).order_by("-created_at")

    context = {
        "hotel": hotel,
        "reviews": reviews,
    }

    return render(request, "hotel_detail.html", context)


# ==========================
# BOOK HOTEL
# ==========================

@login_required
def book_hotel(request, slug):
    hotel = get_object_or_404(Hotel, slug = slug)

    if request.method == "POST":
        check_in = parse_date(request.POST.get("check_in"))
        check_out = parse_date(request.POST.get("check_out"))
        guests = request.POST.get("guests")

        if check_in and check_out and guests:
            booking = Booking.objects.create(
                user=request.user,
                hotel=hotel,
                check_in=check_in,
                check_out=check_out,
                guests=int(guests),
                payment_method="Pay at Hotel"
            )
            
            send_booking_email(booking, request.user.email, request)
        # === EMAIL SENT ===

            messages.success(request, "Booking successful! Pay at hotel.")
            return redirect("confirm_booking", booking_id=booking.id)

        messages.error(request, "Please fill all booking details.")

    return render(request, "booking.html", {"hotel": hotel})


# ==========================
# CONFIRM BOOKING
# ==========================

@login_required
def confirm_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    nights = (booking.check_out - booking.check_in).days
    total_price = nights * booking.hotel.price_per_night * booking.guests

    context = {
        "booking": booking,
        "nights": nights,
        "total_price": total_price,
    }

    return render(request, "confirm_booking.html", context)


# ==========================
# MY BOOKINGS
# ==========================

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "my_bookings.html", {"bookings": bookings})


# ==========================
# BLOGS
# ==========================

def blog_list(request):
    blogs = Blog.objects.all().order_by("-published_at")
    return render(request, "blog_list.html", {"blogs": blogs})


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, "blog_detail.html", {"blog": blog})


# ==========================
# ADD REVIEW
# ==========================

@login_required
def add_review(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:
            Review.objects.create(
                hotel=hotel,
                user=request.user,
                rating=int(rating),
                comment=comment
            )
            messages.success(request, "Review added successfully!")
        else:
            messages.error(request, "Please fill all fields.")
        return redirect('hotel_detail', slug = slug) 

    return redirect("hotel_detail", slug = slug)


# ==========================
# CONTACT
# ==========================

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message
            )
            messages.success(request, "Message sent successfully!")
            return redirect("contact")

        messages.error(request, "Please fill all fields.")

    return render(request, "contact.html")


# ==========================
# AUTH
# ==========================
def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        # DEBUG
        print(f"POST received: {username}, {email}, {password}, {password2}")

        # Password check
        if password != password2:
            messages.error(request, "Passwords do not match.")
            print("Passwords do not match")
            return render(request, 'register.html')

        # Username check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            print("Username already taken")
            return render(request, 'register.html')

        # Email check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            print("Email already registered")
            return render(request, 'register.html')

        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            print(f"User created: {user}")
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            print(f"Exception in user creation: {e}")
            return render(request, 'register.html')

        # Send OTP
        try:
            send_otp_email(user)
            print(f"OTP sent to {user.email}")
        except Exception as e:
            messages.error(request, f"Error sending OTP: {str(e)}")
            print(f"Exception in sending OTP: {e}")
            return render(request, 'register.html')

        # Redirect to OTP verification page
        return redirect('otp_verify', user_id=user.id)

    # GET request
    return render(request, 'register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            send_otp_email(user)
            return redirect("otp_verify", user_id=user.id)
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home")




def otp_verify(request, user_id):
    user = get_object_or_404(User, id=user_id)
    error = None

    if request.method == "POST":
        otp_input = request.POST.get("otp")
        otp_obj = EmailOTP.objects.filter(user=user, otp=otp_input, is_verified=False).first()

        if otp_obj:
            if otp_obj.is_expired():
                error = "OTP expired. Please request a new one."
            else:
                otp_obj.is_verified = True
                otp_obj.save()
                
                
                from django.contrib.auth import login, get_backends
                backend = get_backends()[0].__class__.__module__ + "." + get_backends()[0].__class__.__name__
                login(request, user, backend=backend)
               
                
                return redirect("home")
        else:
            error = "Invalid OTP"

    return render(request, "otp_verify.html", {"error": error, "user": user})



def send_booking_email(booking, user_email, request):
    pdf_buffer = generate_booking_pdf(booking)
    
    subject = "Your Booking is Confirmed!"
    body = f"""
    Hi {booking.user.username},
    
    Your booking at {booking.hotel.name} is confirmed.
    
    Check your bookings here: {request.build_absolute_uri(reverse('my_bookings'))}
    
    Booking ID: {booking.id}
    """
    
    email = EmailMessage(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )
    email.attach(f"Booking_{booking.id}.pdf", pdf_buffer.read(), 'application/pdf')
    email.send()


def resend_otp(request, user_id):
    user = get_object_or_404(User, id=user_id)
    send_otp_email(user)
    messages.success(request, "OTP resent! Check your email.")
    return redirect("otp_verify", user_id=user.id)