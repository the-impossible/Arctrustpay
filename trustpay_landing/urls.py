# My Django imports
from django.urls import path, include

app_name = 'landing'

# My App imports
from trustpay_landing.views import *

# URL patterns for the trustpay_landing app
urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('contact', ContactUsView.as_view(), name="contact"),
    path('about', AboutUsView.as_view(), name="about"),
    path('services', ServicesView.as_view(), name="services"),
]
