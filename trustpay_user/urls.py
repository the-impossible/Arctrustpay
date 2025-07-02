# My Django imports
from django.urls import path, include

app_name = 'user'

# My App imports
from trustpay_user.views import *

# URL patterns for the trustpay_users app
urlpatterns = [
    path('dashboard', DashboardPageView.as_view(), name="dashboard"),
    path('account_details', UserAccountPageView.as_view(), name="account_details"),
    path('account_manager', AccountManagerView.as_view(), name="account_manager"),
]
