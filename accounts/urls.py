"""
URL configuration for the accounts app.

Defines URL patterns for account-related views.

Attributes:
    urlpatterns (list): URL patterns for user registration, account activation, and login.
        - 'registration-user/': User registration view.
        - 'activate/<uidb64>/<token>/': Account activation view.
        - 'user-login/': User login view.
"""
# URL patterns for the accounts
from django.urls import path
from . import views
urlpatterns = [
    path('registration-user/',views.user_registration.as_view()),
    path('activate/<uidb64>/<token>/', views.ActivateAccount.as_view(), name='activate-account'),
    path('user-login/',views.UserLogin.as_view(),name='user-login'),
]