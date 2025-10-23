from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from .models import Signup
from .forms import SignupForm, ForgotPasswordForm, ResetPasswordForm

# ---------- Signup ----------
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            messages.success(request, "✅ Account created successfully. Please login.")
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})

# ---------- Signin ----------
# def signin_view(request):
#     if request.method == "POST":
#         form = SigninForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             try:
#                 user = Signup.objects.get(email=email)
#                 if user.check_password(password):
#                     request.session['user_id'] = user.id
#                     messages.success(request, f"👋 Welcome, {user.name}!")
#                     return redirect('dashboard')
#                 else:
#                     messages.error(request, "❌ Invalid password.")
#             except Signup.DoesNotExist:
#                 messages.error(request, "❌ User not found.")
#     else:
#         form = SigninForm()
#     return render(request, "signin.html", {"form": form})



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password  # For password verification
from .models import Signup  # Your Signup model
from .forms import LoginForm  # Your LoginForm


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Signup
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            try:
                # Try email first
                user = Signup.objects.filter(email=identifier).first()
                
                # If not found by email, try name
                if not user:
                    user = Signup.objects.filter(name=identifier).first()

                if not user:
                    messages.error(request, 'No account found with that email or name.')
                    return render(request, 'login.html', {'form': form})

                # Check password
                if check_password(password, user.password):
                    # Store in session
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    request.session['user_email'] = user.email

                    # Admin check
                    if user.email == 'lakshmi@kvktechnoid.com':
                        messages.success(request, f'Welcome Admin {user.name}!')
                        return redirect('admin_dashboard')
                    else:
                        messages.success(request, f'Welcome back {user.name}!')
                        return redirect('home')
                else:
                    messages.error(request, 'Invalid password.')
            except Exception as e:
                messages.error(request, 'Error during login. Try again.')

    else:
        form = LoginForm()
        # Clear old session
        request.session.flush()

    return render(request, 'login.html', {'form': form})

def signup_list(request):
    users = Signup.objects.all()
    return render(request, 'signup_list.html', {'users': users})


# ---------- Dashboard ----------

from django.shortcuts import render, redirect
from collections import defaultdict
from .models import Meeting, Signup  # adjust model import if needed

def home(request):
    # ✅ Check login
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    # ✅ Fetch user info
    try:
        user = Signup.objects.get(id=user_id)
    except Signup.DoesNotExist:
        request.session.flush()
        return redirect('login')

    # ✅ Fetch all meetings and group by date
    meetings = Meeting.objects.all().order_by('-date', '-event_time')
    meetings_by_date = defaultdict(list)
    for meeting in meetings:
        meetings_by_date[meeting.date].append(meeting)

    # ✅ Pass both user & meetings to template
    context = {
        'user': user,
        'meetings_by_date': dict(meetings_by_date),
    }

    return render(request, 'home.html', context)


from django.contrib.auth.decorators import login_required  # Optional: But since we use sessions, manual check below

def admin_dashboard_view(request):
    # Manual auth check using session (matches your setup)
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please log in first.')
        return redirect('login')
    
    try:
        user = Signup.objects.get(id=user_id)
        # Optional: Verify it's the admin user
        if user.email != 'lakshmi@kvktechnoid.com':
            messages.error(request, 'Access denied. Admin only.')
            return redirect('home')
    except Signup.DoesNotExist:
        request.session.flush()  # Clear invalid session
        return redirect('login')
    
    # Fetch data for dashboard (e.g., all users)
    all_users = Signup.objects.all().order_by('-id')  # Latest first
    context = {
        'user': user,
        'all_users': all_users,  # For displaying user list
        'total_users': all_users.count(),
    }
    return render(request, 'admin_dashboard.html', context)


def logout_view(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('login')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Signup  # Your user model

def get_current_user(request):
    """Helper to fetch current user from session."""
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return Signup.objects.get(id=user_id)
    except Signup.DoesNotExist:
        request.session.flush()  # Clear invalid session
        return None

def edit_user(request, user_id):
    # Auth check: Only logged-in admins can edit
    current_user = get_current_user(request)
    if not current_user:
        messages.error(request, 'Please log in to access this page.')
        return redirect('login')
    
    # Fetch the user to edit (add permission check if needed, e.g., current_user.is_admin)
    user = get_object_or_404(Signup, id=user_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')

        # Basic validation (extend as needed)
        if not name or not email:
            messages.error(request, 'Name and email are required.')
            return render(request, 'edit_user.html', {'user': user, 'current_user': current_user})

        user.name = name
        user.email = email
        user.mobile_number = mobile_number
        user.save()
        messages.success(request, f'User "{user.name}" updated successfully!')
        return redirect('signup_list')

    context = {
        'user': user,  # User to edit
        'current_user': current_user,  # For navbar
    }
    return render(request, 'edit_user.html', context)

def delete_user(request, user_id):
    # Auth check
    current_user = get_current_user(request)
    if not current_user:
        messages.error(request, 'Please log in to access this page.')
        return redirect('login')
    
    user = get_object_or_404(Signup, id=user_id)
    
    # Optional: Prevent self-deletion or admin deletion
    if user.id == current_user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('signup_list')
    
    user_name = user.name  # Save name before delete
    user.delete()
    messages.success(request, f'User "{user_name}" deleted successfully!')
    return redirect('signup_list')













def dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect('signin')
    user = Signup.objects.get(id=user_id)
    return render(request, "dashboard.html", {"user": user})

# ---------- Forgot Password --------
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .models import Signup, PasswordResetOTP
import random

# Step 1: Send OTP
def forgot_password_send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = Signup.objects.get(email=email)
        except Signup.DoesNotExist:
            messages.error(request, "❌ Email not registered.")
            return redirect('forgot_password_send_otp')

        otp = str(random.randint(100000, 999999))
        PasswordResetOTP.objects.create(email=email, otp=otp)

        # Send OTP via email
        send_mail(
            subject='🔐 Your OTP for Password Reset',
            message=f'Your OTP is {otp}. It will expire in 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

        request.session['reset_email'] = email
        messages.success(request, f"✅ OTP sent to {email}. Check your inbox.")
        return redirect('verify_otp')

    return render(request, 'forgot_password.html')


# Step 2: Verify OTP
def verify_otp(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, "Session expired. Try again.")
        return redirect('forgot_password_send_otp')

    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        try:
            otp_entry = PasswordResetOTP.objects.filter(email=email).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            messages.error(request, "OTP not found. Please resend.")
            return redirect('forgot_password_send_otp')

        if otp_entry.otp == otp_entered and otp_entry.is_valid():
            messages.success(request, "✅ OTP verified! Set your new password.")
            request.session['otp_verified'] = True
            return redirect('create_new_password')
        else:
            messages.error(request, "❌ Invalid or expired OTP.")
            return redirect('verify_otp')

    return render(request, 'verify_otp.html')


# Step 3: Create new password
def create_new_password(request):
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified', False)

    if not email or not otp_verified:
        messages.error(request, "Session expired or not verified.")
        return redirect('forgot_password_send_otp')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "⚠️ Passwords do not match.")
            return redirect('create_new_password')

        user = Signup.objects.get(email=email)
        user.password = make_password(password)
        user.save()

        # Clear session
        del request.session['reset_email']
        del request.session['otp_verified']

        messages.success(request, "✅ Password reset successful! You can now sign in.")
        return redirect('login')

    return render(request, 'create_new_password.html')




from django.shortcuts import render, redirect
# from django.contrib import messages
# from .forms import LocationAssignmentForm
# from .models import LocationAssignment

# def assign_location(request):
#     if request.method == "POST":
#         form = LocationAssignmentForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "✅ Location assigned successfully!")
#             return redirect('view_assignments')
#     else:
#         form = LocationAssignmentForm()
#     return render(request, "assign_location.html", {"form": form})


# def view_assignments(request):
#     assignments = LocationAssignment.objects.select_related("user").order_by("-date")
#     return render(request, "view_assignments.html", {"assignments": assignments})

from django.shortcuts import render, redirect
from .models import LocationAssignment, Signup
from .forms import LocationAssignmentForm

def add_assignment(request):
    # Fetch logged-in user from session
    user_id = request.session.get('user_id')
    user = None
    if user_id:
        try:
            user = Signup.objects.get(id=user_id)
        except Signup.DoesNotExist:
            request.session.flush()
            return redirect('login')

    # Get all assigned dates
    qs = LocationAssignment.objects.values_list('date', flat=True)
    taken_dates = [d.strftime('%Y-%m-%d') for d in qs]

    # Handle form submission
    if request.method == "POST":
        form = LocationAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("add_assignment")
    else:
        form = LocationAssignmentForm()

    return render(request, "add_assignment.html", {
        "form": form,
        "taken_dates": taken_dates,
        "user": user,  # ✅ Pass user to template
    })



from django.shortcuts import render, redirect
from .models import LocationAssignment, Signup

def assignment_list(request):
    """Display all assignments along with logged-in user info"""
    # Fetch logged-in user from session
    user_id = request.session.get('user_id')
    user = None
    if user_id:
        try:
            user = Signup.objects.get(id=user_id)
        except Signup.DoesNotExist:
            request.session.flush()
            return redirect('login')

    # Get all assignments
    assignments = LocationAssignment.objects.all().order_by('-id')

    return render(request, 'assignment_list.html', {
        'assignments': assignments,
        'user': user,  # Pass user to template
    })


import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import LocationAssignment, Signup
from .forms import LocationAssignmentForm
import json

def edit_assignment(request, pk):
    """Edit an existing assignment"""
    # Fetch logged-in user
    user_id = request.session.get('user_id')
    user = None
    if user_id:
        try:
            user = Signup.objects.get(id=user_id)
        except Signup.DoesNotExist:
            request.session.flush()
            return redirect('login')

    assignment = get_object_or_404(LocationAssignment, pk=pk)
    
    if request.method == 'POST':
        form = LocationAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Assignment updated successfully.")
            return redirect('assignment_list')
    else:
        form = LocationAssignmentForm(instance=assignment)

    # Exclude current record while fetching already booked dates
    taken_dates = list(LocationAssignment.objects.exclude(id=pk).values_list('date', flat=True))
    taken_dates = [d.strftime("%Y-%m-%d") for d in taken_dates]

    return render(request, 'add_assignment.html', {
        'form': form,
        'taken_dates': json.dumps(taken_dates),
        'edit_mode': True,
        'user': user,  # Pass logged-in user to template
    })


def delete_assignment(request, pk):
    """Delete an assignment"""
    # Fetch logged-in user
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('signin')

    assignment = get_object_or_404(LocationAssignment, pk=pk)
    assignment.delete()
    messages.success(request, "🗑️ Assignment deleted successfully.")
    return redirect('assignment_list')





# create meeting

def check_location(request):
    # Fetch logged-in user
    user_id = request.session.get('user_id')
    user = None
    if user_id:
        try:
            user = Signup.objects.get(id=user_id)
        except Signup.DoesNotExist:
            request.session.flush()
            return redirect('login')
    else:
        return redirect('login')

    return render(request, "check_location.html", {
        'user': user,  # Pass user to template
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
from .models import Meeting, LocationAssignment


# from django.http import JsonResponse
# from .models import LocationAssignment, Meeting
# import datetime

# def get_location(request):
#     date_str = request.GET.get("date")

#     if not date_str:
#         return JsonResponse({"error": "Missing date"}, status=400)

#     try:
#         date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
#     except ValueError:
#         return JsonResponse({"error": "Invalid date format"}, status=400)

#     # Get assigned persons/locations for that date
#     assignments = LocationAssignment.objects.filter(date=date).select_related("user")

#     data = []
#     for assign in assignments:
#         # Get booked meetings for this person/location/date
#         meetings = Meeting.objects.filter(
#             date=date,
#             name=assign.user.name,
#             location=assign.location
#         ).order_by("event_time")

#         booked_slots = []
#         for meet in meetings:
#             start = meet.event_time.strftime("%H:%M") if meet.event_time else ""
#             end = ""
#             if meet.event_time and meet.duration:
#                 end_time = (
#                     datetime.datetime.combine(date, meet.event_time)
#                     + datetime.timedelta(hours=meet.duration)
#                 ).time()
#                 end = end_time.strftime("%H:%M")

#             booked_slots.append({
#                 "subject": meet.subject or "",
#                 "agenda": meet.agenda or "",
#                 "event_time": start,
#                 "endtime": end,
#                 "duration": meet.duration or "",
#             })

#         data.append({
#             "id": assign.id,
#             "name": assign.user.name,
#             "location": assign.location,
#             "booked_slots": booked_slots,
#         })

#     return JsonResponse({"locations": data})

# # app/views.py (full file for completeness)
# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.db import OperationalError  # Added for DB-specific errors
# from .models import LocationAssignment, Meeting
# from .forms import LocationAssignmentForm
# import datetime



# #  locked the booked timings

# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.db.utils import OperationalError
# from .models import Meeting
# import datetime


# def is_slot_available(date, event_time, duration, exclude_id=None):
#     """Check if slot overlaps with existing meetings"""
#     if not event_time or not duration:
#         return True

#     dt_start = datetime.datetime.combine(date, event_time)
#     dt_end = dt_start + datetime.timedelta(hours=duration)

#     conflicts = Meeting.objects.filter(date=date).exclude(id=exclude_id)
#     for m in conflicts:
#         if not m.event_time or not m.duration:
#             continue
#         existing_start = datetime.datetime.combine(m.date, m.event_time)
#         existing_end = existing_start + datetime.timedelta(hours=m.duration)
#         # Overlap check
#         if dt_start < existing_end and dt_end > existing_start:
#             return False
#     return True


# # @csrf_exempt
# from django.http import JsonResponse
# from django.db import OperationalError
# from django.views.decorators.csrf import csrf_exempt
# from .models import Meeting
# import datetime

# @csrf_exempt
# def update_location(request):
#     if request.method == "POST":
#         try:
#             # --- Fetch Data ---
#             meeting_id = request.POST.get("id")
#             date_str = request.POST.get("date")
#             name = request.POST.get("name")
#             location = request.POST.get("location")
#             subject = request.POST.get("subject")
#             agenda = request.POST.get("agenda")
#             event_time_str = request.POST.get("event_time")
#             duration_str = request.POST.get("duration")
#             referred_by = request.POST.get("referred_by")
#             place_of_event = request.POST.get("place_of_event")
#             contact_number = request.POST.get("contact_number")
#             invite_name = request.POST.get("invite_name")

#             # --- Validation ---
#             if not all([date_str, name, location, event_time_str, duration_str]):
#                 return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

#             if contact_number and not contact_number.isdigit():
#                 return JsonResponse({"status": "error", "message": "Contact number must contain only digits"}, status=400)
#             if contact_number and len(contact_number) != 10:
#                 return JsonResponse({"status": "error", "message": "Contact number must be 10 digits long"}, status=400)

#             # --- Parse Dates ---
#             date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
#             event_time_obj = datetime.datetime.strptime(event_time_str, "%H:%M").time()
#             duration = float(duration_str)

#             # --- Check Slot Availability ---
#             if not is_slot_available(date_obj, event_time_obj, duration, meeting_id):
#                 return JsonResponse({
#                     "status": "error",
#                     "message": "This time slot has already been booked! Please check above booked time slots."
#                 }, status=400)

#             # --- Create or Update Meeting ---
#             meeting = Meeting.objects.filter(id=meeting_id).first() if meeting_id else Meeting()

#             meeting.date = date_obj
#             meeting.name = name
#             meeting.location = location
#             meeting.subject = subject or None
#             meeting.agenda = agenda or None
#             meeting.event_time = event_time_obj
#             meeting.duration = duration
#             meeting.referred_by = referred_by or None
#             meeting.place_of_event = place_of_event or None
#             meeting.contact_number = contact_number or None
#             meeting.invite_name = invite_name or None

#             meeting.save()

#             return JsonResponse({
#                 "status": "success",
#                 "message": "✅ Meeting saved successfully!",
#                 "id": meeting.id,
#                 "endtime": str(meeting.endtime) if hasattr(meeting, 'endtime') else None,
#             })

#         except ValueError as e:
#             return JsonResponse({"status": "error", "message": f"Invalid data: {e}"}, status=400)

#         except OperationalError as e:
#             return JsonResponse({"status": "error", "message": f"Database error: {e}"}, status=500)

#         except Exception as e:
#             return JsonResponse({"status": "error", "message": f"Server error: {e}"}, status=500)

#     return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

from django.http import JsonResponse
from django.db import OperationalError
from django.views.decorators.csrf import csrf_exempt
from .models import Meeting, LocationAssignment
from datetime import datetime, timedelta  # ✅ fixed import


def get_location(request):
    """Fetch assigned locations and booked meetings for a given date."""
    date_str = request.GET.get("date")

    if not date_str:
        return JsonResponse({"error": "Missing date"}, status=400)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()  # ✅ fixed
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)

    # Get assigned persons/locations for that date
    assignments = LocationAssignment.objects.filter(date=date).select_related("user")

    data = []
    for assign in assignments:
        # Get booked meetings for this person/location/date
        meetings = Meeting.objects.filter(
            date=date,
            name=assign.user.name,
            location=assign.location
        ).order_by("event_time")

        booked_slots = []
        for meet in meetings:
            start = meet.event_time.strftime("%H:%M") if meet.event_time else ""
            end = ""
            if meet.event_time and meet.duration:
                end_time = (
                    datetime.combine(date, meet.event_time)
                    + timedelta(hours=meet.duration)
                ).time()
                end = end_time.strftime("%H:%M")

            booked_slots.append({
                "subject": meet.subject or "",
                "agenda": meet.agenda or "",
                "event_time": start,
                "endtime": end,
                "duration": meet.duration or "",
            })

        data.append({
            "id": assign.id,
            "name": assign.user.name,
            "location": assign.location,
            "booked_slots": booked_slots,
        })

    return JsonResponse({"locations": data})


@csrf_exempt
def update_location(request):
    """Create or update a meeting and validate slot availability."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        # --- Fetch Data ---
        meeting_id = request.POST.get("id")
        date_str = request.POST.get("date")
        name = request.POST.get("name")
        location = request.POST.get("location")
        subject = request.POST.get("subject")
        agenda = request.POST.get("agenda")
        event_time_str = request.POST.get("event_time")
        duration_str = request.POST.get("duration")
        referred_by = request.POST.get("referred_by")
        place_of_event = request.POST.get("place_of_event")
        contact_number = request.POST.get("contact_number")
        invite_name = request.POST.get("invite_name")

        # --- Validation ---
        if not all([date_str, name, location, event_time_str, duration_str]):
            return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

        if contact_number and not contact_number.isdigit():
            return JsonResponse({"status": "error", "message": "Contact number must contain only digits"}, status=400)
        if contact_number and len(contact_number) != 10:
            return JsonResponse({"status": "error", "message": "Contact number must be 10 digits long"}, status=400)

        # --- Parse Dates ---
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        event_time_obj = datetime.strptime(event_time_str, "%H:%M").time()
        duration = float(duration_str)

        # --- Check Slot Availability ---
        if not is_slot_available(date_obj, event_time_obj, duration, meeting_id):
            return JsonResponse({
                "status": "error",
                "message": "This time slot has already been booked! Please check above booked time slots."
            }, status=400)

        # --- Create or Update Meeting ---
        meeting = Meeting.objects.filter(id=meeting_id).first() if meeting_id else Meeting()

        meeting.date = date_obj
        meeting.name = name
        meeting.location = location
        meeting.subject = subject or None
        meeting.agenda = agenda or None
        meeting.event_time = event_time_obj
        meeting.duration = duration
        meeting.referred_by = referred_by or None
        meeting.place_of_event = place_of_event or None
        meeting.contact_number = contact_number or None
        meeting.invite_name = invite_name or None

        meeting.save()

        return JsonResponse({
            "status": "success",
            "message": "✅ Meeting saved successfully!",
            "id": meeting.id,
        })

    except ValueError as e:
        return JsonResponse({"status": "error", "message": f"Invalid data: {e}"}, status=400)

    except OperationalError as e:
        return JsonResponse({"status": "error", "message": f"Database error: {e}"}, status=500)

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Server error: {e}"}, status=500)


# ✅ Add a helper function for slot validation if not already defined
def is_slot_available(date, event_time, duration, meeting_id=None):
    """Checks whether the requested slot overlaps with existing meetings."""
    from datetime import datetime, timedelta
    meetings = Meeting.objects.filter(date=date)

    new_start = datetime.combine(date, event_time)
    new_end = new_start + timedelta(hours=duration)

    for m in meetings:
        if meeting_id and m.id == int(meeting_id):
            continue  # Skip the same meeting being edited

        existing_start = datetime.combine(date, m.event_time)
        existing_end = existing_start + timedelta(hours=m.duration)

        # Check for overlap
        if (new_start < existing_end) and (existing_start < new_end):
            return False
    return True


# @csrf_exempt
# def update_location(request):
#     if request.method == "POST":
#         meeting_id = request.POST.get("id")
#         date_str = request.POST.get("date")
#         name = request.POST.get("name")
#         location = request.POST.get("location")
#         subject = request.POST.get("subject")
#         agenda = request.POST.get("agenda")
#         event_time_str = request.POST.get("event_time")
#         duration_str = request.POST.get("duration")


#         if not all([date_str, name, location]):
#             return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

#         try:
#             date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
#             event_time_obj = datetime.datetime.strptime(event_time_str, "%H:%M").time() if event_time_str else None
#             duration = int(duration_str) if duration_str else 0

#             # Check slot availability
#             if not is_slot_available(date_obj, event_time_obj, duration, meeting_id):
#                 return JsonResponse({"status": "error", "message": "This time slot has been already booked! please see the above booked time slots"}, status=400)

#             # Try to update existing meeting, else create a new one
#             meeting = None
#             if meeting_id:
#                 try:
#                     meeting = Meeting.objects.get(id=meeting_id)
#                 except Meeting.DoesNotExist:
#                     # If ID invalid, create a new one
#                     meeting = Meeting()

#             else:
#                 meeting = Meeting()

#             meeting.date = date_obj
#             meeting.name = name
#             meeting.location = location
#             meeting.subject = subject or None
#             meeting.agenda = agenda or None
#             meeting.event_time = event_time_obj
#             meeting.duration = duration
#             meeting.save()

#             return JsonResponse({
#                 "status": "success",
#                 "message": "Meeting saved successfully!",
#                 "id": meeting.id,
#                 "endtime": str(meeting.endtime) if meeting.endtime else None,
#             })

#         except ValueError as e:
#             return JsonResponse({"status": "error", "message": f"Invalid data: {e}"}, status=400)
#         except OperationalError as e:
#             return JsonResponse({"status": "error", "message": f"Database error: {e}"}, status=500)
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": f"Server error: {e}"}, status=500)

#     return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


from django.shortcuts import render, get_object_or_404, redirect
from .models import Meeting
from .forms import MeetingForm  # we'll create this form next
from django.contrib import messages

# def meetings_list(request):
#     meetings = Meeting.objects.all().order_by('-date')
#     return render(request, 'meeting_list.html', {'meetings': meetings})
from django.core.paginator import Paginator
from datetime import datetime
from datetime import datetime, date, timedelta
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Meeting

def meetings_list(request):
    selected_date = request.GET.get('selected_date', '')

    # Get all meetings, ordered by date and event_time (morning → evening)
    meetings = Meeting.objects.all().order_by('-date', 'event_time')

    # Filter by selected date if provided
    if selected_date:
        try:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            meetings = meetings.filter(date=date_obj).order_by('event_time')
        except ValueError:
            pass  # ignore invalid date input

    # Example: to filter only today's meetings
    # today = date.today()
    # meetings = meetings.filter(date=today).order_by('event_time')

    # Pagination
    paginator = Paginator(meetings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'meetings': page_obj,
        'selected_date': selected_date,
    }
    return render(request, 'meeting_list.html', context)


# def meetings_list(request):
#     meetings = Meeting.objects.all().order_by('-date')  # Latest first

#     # Get selected_date from GET request
#     selected_date = request.GET.get('selected_date', '')

#     if selected_date:
#         try:
#             date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
#             meetings = meetings.filter(date=date_obj)  # Exact match
#         except ValueError:
#             pass  # Ignore invalid date
#     # else: no date selected → show all meetings

#     paginator = Paginator(meetings, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     context = {
#         'meetings': page_obj,
#         'selected_date': selected_date,
#     }
#     return render(request, 'meeting_list.html', context)



def meeting_detail(request, id):
    meeting = get_object_or_404(Meeting, id=id)
    return render(request, 'meeting_detail.html', {'meeting': meeting})

def edit_meeting(request, id):
    meeting = get_object_or_404(Meeting, id=id)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Meeting updated successfully.")
            return redirect('meetings_list')
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'edit_meeting.html', {'form': form, 'meeting': meeting})

def delete_meeting(request, id):
    meeting = get_object_or_404(Meeting, id=id)
    meeting.delete()
    messages.success(request, "🗑️ Meeting deleted successfully.")
    return redirect('meetings_list')



# download the meetings selected one 
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from .models import Meeting


def download_meetings_pdf(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_meetings')
        if not selected_ids:
            return HttpResponse("No meetings selected")

        meetings = Meeting.objects.filter(id__in=selected_ids)

        # --- Create PDF Response ---
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="meetings.pdf"'

        doc = SimpleDocTemplate(
            response,
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=60,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()
        elements = []

        # --- subject ---
        subject_style = ParagraphStyle(
            name='subjectStyle',
            fontSize=18,
            leading=22,
            alignment=1,  # center
            textColor=colors.HexColor("#0d6efd"),
            spaceAfter=20,
        )
        # elements.append(Paragraph("📅 Selected Meetings", subject_style))
        elements.append(Paragraph("📅 Today Meetings", subject_style))

        elements.append(Spacer(1, 0.2 * inch))

        # --- Table Data ---
        data = [["S.No", "Date", "event_time", "Event"]]

        for index, m in enumerate(meetings, start=1):
            data.append([
                str(index),
                str(m.date or ""),
                str(m.event_time or ""),
                str(m.subject or ""),
            ])

        # --- Create Table ---
        table = Table(data, colWidths=[50, 120, 120, 200])

        # --- Table Styling ---
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#007bff")),  # Header bg
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.grey),
        ])

        # --- Alternating Row Colors ---
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#E9F3FF"))
            else:
                style.add('BACKGROUND', (0, i), (-1, i), colors.whitesmoke)

        table.setStyle(style)
        elements.append(table)

        # --- Build PDF ---
        doc.build(elements)
        return response

    return HttpResponse("Invalid request method.")
