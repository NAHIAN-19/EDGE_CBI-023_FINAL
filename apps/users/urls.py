from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # API endpoints
    path('api/users/register/', views.UserRegistrationView.as_view(), name='user-registration'),
    path('api/users/login/', views.UserLoginView.as_view(), name='user-login'),
    path('api/users/logout/', views.LogoutView.as_view(), name='user-logout'),
    path('api/users/profile/', views.ProfileView.as_view(), name='user-profile'),
    path('api/users/profile/<int:user_id>/', views.ProfileView.as_view(), name='user-profile-detail'),
    
    # Template views
    path('register/', TemplateView.as_view(template_name='users/register.html'), name='register'),
    path('login/', TemplateView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', TemplateView.as_view(template_name='users/logout.html'), name='logout'),
]