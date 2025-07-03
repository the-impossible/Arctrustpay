from django.conf import settings
from django.core.exceptions import ValidationError

# My app imports
from trustpay_user.models import *
from trustpay_trx.models import *

def trx_context(request):
    context = {}

    try:
        context['user_balance'] = Balance.objects.filter(user=request.user).first().amount
    except AttributeError:
        context['user_balance'] = '0'
    except ValidationError:
        pass


    return context
