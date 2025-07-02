# My django imports
from django.contrib.auth.models import AnonymousUser
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from trustpay_trx.models import *
from trustpay_trx import views

# My app imports

# Determining if the internal transfer variable is in session
def is_admin(func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not authorized to view that page')
            return redirect('user:dashboard')
    return wrapper_func
