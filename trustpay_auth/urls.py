# My Django imports
from django.urls import path, include

app_name = 'auth'

# My App imports
from trustpay_auth.views import *

# URL patterns for the trustpay_landing app
urlpatterns = [
    path('login', LoginPageView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('register', RegisterPageView.as_view(), name="register"),
    path('forget-password', ForgotPasswordPageView.as_view(), name="forget-password"),
    path('reset-password//<uidb64>/<token>', ResetPasswordPageView.as_view(), name="reset-password"),
    path('signout', SignOutPageView.as_view(), name="signout"),
    path('welcome', EmailPreviewPageView.as_view(), name="welcome"),
]
