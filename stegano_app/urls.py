from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import (
    feedback_view,
    CustomPasswordResetConfirmView,
    share_view,  # ✅ Correct import here
)

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('encrypt/', views.encrypt_view, name='encrypt'),
    path('decrypt/', views.decrypt_view, name='decrypt'),
    path('help/', views.help_view, name='help'),
    path('about/', views.about_view, name='about'),  # ✅ Add this line
    path('feedback/', feedback_view, name='feedback'),
    path('share/<str:image_name>/', share_view, name='share'),
    path('send-encrypted-email/', views.send_encrypted_email_view, name='send_encrypted_email'),

    # Password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),

  path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(
    template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

