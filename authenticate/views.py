from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from mains.models import Illustration


# Create your views here.

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'authenticate_templates/register.html',{'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, 'authenticate_templates/login.html')

        user = authenticate(request, email=email, password=password)  # Authenticate using email
        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in.")
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'authenticate_templates/login.html')


@login_required
def logout_view(request):
    if request.method == 'POST':

        request.session.flush()
        logout(request)
        messages.success(request, "you have been logged out.")
        return redirect('login')
    
    return render (request, 'authenticate_templates/logout.html')


def home_view(request):

    illustrations = Illustration.objects.all().order_by('-uploaded_at')[:5]
    live_bidding_illustrations = Illustration.objects.filter(is_bidding_active=True)
    return render(request, 'main_templates/home.html',{
        'illustrations': illustrations,
        'live_bidding_illustrations': live_bidding_illustrations
    })


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('illustrator_profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    if user.user_type == 'illustrator':
        return render(request, 'authenticate_templates/illustrator_profile.html', {'form': form})
    else:
        return render(request, 'authenticate_templates/simple_user_profile.html', {'form': form})


from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .models import CustomUser

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get("email", '')
        try:
            user = CustomUser.objects.get(email=email)

            # Generate password reset token

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build password reset link
            current_site = get_current_site(request)
            reset_url = f"http://{current_site.domain}/reset-password/{uid}/{token}/"

            #send email
            subject = "Password Reset Request"
            message = f'Please click the following link to reset password: {reset_url}'
            send_mail(
                subject,
                message,
                'noreply@yourdomain.com',
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No user found with this email address.')

    return render (request, "authenticate_templates/forgot_password.html")



def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 and password2 and password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request, 'Password has been reset successfully.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
        return render(request, 'authenticate_templates/reset_password.html')
    else:
        messages.error(request, 'Password reset link is invalid or has expired.')
        return redirect('login')
            

        