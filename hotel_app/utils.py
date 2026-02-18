from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP

def generate_booking_pdf(booking):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(200, 800, "Booking Confirmation")
    
    # Booking info
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Booking ID: {booking.id}")
    c.drawString(50, 730, f"Hotel: {booking.hotel.name}")
    c.drawString(50, 710, f"Check-in: {booking.check_in}")
    c.drawString(50, 690, f"Check-out: {booking.check_out}")
    c.drawString(50, 670, f"Guests: {booking.guests}")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def send_otp_email(user):
    from .models import EmailOTP

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Save OTP
    EmailOTP.objects.create(user=user, otp=otp)
    
    # Send email
    send_mail(
        'Your OTP Code',
        f'Hello {user.username}, your OTP code is: {otp}\nIt is valid for 5 minutes.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    
