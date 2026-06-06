from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth import get_user_model
from .forms import FeedbackForm
from .models import Feedback
from PIL import Image
import os
import stepic
import mimetypes
from django.urls import reverse_lazy


# Home
def home_view(request):
    return render(request, 'home.html')


# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


# Register
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

        # Generate activation token and link
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f"{request.scheme}://{request.get_host()}{reverse('activate', kwargs={'uidb64': uid, 'token': token})}"

        subject = 'Activate Your Account'
        html_content = render_to_string('activation_email.html', {
            'username': username,
            'activation_link': activation_link,
        })
        plain_text = f"Hello {username},\n\nPlease activate your account:\n{activation_link}"

        send_mail(
            subject,
            plain_text,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_content
        )

        messages.success(request, "Account created! Check your email to activate.")
        return redirect('login')

    return render(request, 'register.html')


# Activate Account
def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated! You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect('home')


# Logout
def logout_view(request):
    logout(request)
    return redirect('home')


# Dashboard
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')


@login_required
def encrypt_view(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        secret_text = request.POST.get('text')
        key = request.POST.get('key')

        if image_file and secret_text and key:
            if not image_file.content_type.startswith('image/'):
                return render(request, 'encrypt.html', {
                    'message': "Uploaded file is not a valid image."
                })

            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_path = fs.path(filename)

            try:
                image = Image.open(image_path).convert("RGB")
                combined_message = f"{key}:{secret_text}"
                encoded_image = stepic.encode(image, combined_message.encode())

                encoded_filename = f"encoded_{os.path.splitext(filename)[0]}.png"
                encoded_path = os.path.join(fs.location, encoded_filename)
                encoded_image.save(encoded_path, format="PNG")

                # ✅ THIS IS THE CHANGE: redirect to share.html
                return redirect('share', image_name=encoded_filename)

            except Exception as e:
                return render(request, 'encrypt.html', {
                    'message': f"Encryption failed: {str(e)}"
                })

            finally:
                if os.path.exists(image_path):
                    os.remove(image_path)

        else:
            return render(request, 'encrypt.html', {
                'message': "Please upload an image, enter a message, and provide a key."
            })

    return render(request, 'encrypt.html')



# Decrypt Image
@login_required
def decrypt_view(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        entered_key = request.POST.get('key')

        if image_file and entered_key:
            if not image_file.content_type.startswith('image/'):
                return render(request, 'decrypt.html', {
                    'message': "Uploaded file is not a valid image."
                })

            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            file_path = fs.path(filename)

            try:
                img = Image.open(file_path).convert("RGB")
                decoded_data = stepic.decode(img)

                if ':' in decoded_data:
                    key, hidden_message = decoded_data.split(':', 1)
                    if key == entered_key:
                        return render(request, 'decrypt.html', {
                            'message': "Image decrypted successfully!",
                            'hidden_message': hidden_message
                        })
                    else:
                        return render(request, 'decrypt.html', {
                            'message': "Incorrect decryption key."
                        })
                else:
                    return render(request, 'decrypt.html', {
                        'message': "No valid hidden message found."
                    })

            except Exception as e:
                return render(request, 'decrypt.html', {
                    'message': f"Decryption failed: {str(e)}"
                })

            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            return render(request, 'decrypt.html', {
                'message': "Please upload an image and enter a key."
            })

    return render(request, 'decrypt.html')


# About Page
def about_view(request):
    return render(request, 'about.html')


# Help Page
def help_view(request):
    return render(request, 'help.html')


# Feedback Page
def feedback_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        Feedback.objects.create(name=name, email=email, message=message)
        messages.success(request, 'Thank you for your feedback!')
        return redirect('feedback')

    return render(request, 'feedback.html')

@login_required
def send_encrypted_email_view(request):
    if request.method == "POST":
        recipient = request.POST.get('recipient')
        image_name = request.POST.get('image_url', '').strip().lstrip('/')

        if not (recipient and image_name):
            messages.error(request, "Missing recipient or image.")
            return redirect('encrypt')

        image_path = os.path.join(settings.MEDIA_ROOT, image_name)

        print("Image Path:", image_path)

        if not os.path.exists(image_path):
            messages.error(request, f"Image not found at {image_path}.")
            return redirect('encrypt')

        try:
            mail = EmailMessage(
                subject='🔐 Your Encrypted Image from StegoEncrypt',
                body='Attached is your encrypted image. Visit our site to decrypt it.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient]
            )
            mime_type, _ = mimetypes.guess_type(image_path)
            with open(image_path, 'rb') as img:
                mail.attach(image_name, img.read(), mime_type or 'application/octet-stream')
            mail.send()

            messages.success(request, f"Encrypted image sent to {recipient}.")
            return redirect('share', image_name=image_name)
        except Exception as e:
            messages.error(request, f"Failed to send email: {str(e)}")
            return redirect('share', image_name=image_name)





# Share Encrypted Image Page
@login_required
def share_view(request, image_name):
    image_url = settings.MEDIA_URL + image_name
    full_url = request.build_absolute_uri(image_url)
    return render(request, 'share.html', {
        'image_url': image_url,
        'full_url': full_url,
    })

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        print("✅ form_valid triggered")
        response = super().form_valid(form)
        messages.success(self.request, "✅ Your password has been successfully changed. Please log in.")
        return response


    def form_valid(self, form):
        messages.success(self.request, "Your password has been successfully changed. Please log in.")
        return super().form_valid(form)
