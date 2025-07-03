# My django imports
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.contrib import messages

# My app imports
from trustpay_trx.models import *
from trustpay_auth.models import *

def has_updated(func):
    def wrapper_func(request, *args, **kwargs):
        try:
            user = User.objects.get(username=request.user).personal_info.first_name
            if user :
                return func(request, *args, **kwargs)

            messages.info(request, 'You need to update your profile first')
            return redirect('user:account_details')

        except User.DoesNotExist:
            messages.info(request, 'User not found!')
            return redirect('auth:login')

        except ObjectDoesNotExist:
            messages.info(request, 'You need to update your profile first')
            return redirect('user:account_details')

    return wrapper_func
