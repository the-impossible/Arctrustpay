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
def has_transaction_pin(func):
    def wrapper_func(request, *args, **kwargs):
        try:
            TransactionPin.objects.get(user=request.user)
            return func(request, *args, **kwargs)
        except TransactionPin.DoesNotExist:
            messages.info(request, 'You are need to create a transaction pin first')
            return redirect('user:account_details')
    return wrapper_func

def has_transfer_data(func):
    def wrapper_func(request, *args, **kwargs):
        if 'transfer_data' in request.session:
            return func(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not authorized to view that page')
            return redirect('trx:internal_transfer')
    return wrapper_func

def has_ach_data(func):
    def wrapper_func(request, *args, **kwargs):
        if 'ach_data' in request.session:
            return func(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not authorized to view that page')
            return redirect('trx:ach_transfer')
    return wrapper_func

def has_domestic_data(func):
    def wrapper_func(request, *args, **kwargs):
        if 'd_wire_data' in request.session:
            return func(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not authorized to view that page')
            return redirect('trx:d_wire_transfer')
    return wrapper_func

def has_international_data(func):
    def wrapper_func(request, *args, **kwargs):
        if 'f_wire_data' in request.session:
            return func(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not authorized to view that page')
            return redirect('trx:f_wire_transfer')
    return wrapper_func
