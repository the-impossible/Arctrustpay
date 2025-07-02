from django.conf import settings
from django.core.exceptions import ValidationError
from trustpay_user.models import *

def global_context(request):
    context = {}

    context['app_name'] = settings.APP_NAME
    try:
        context['tPin'] = TransactionPin.objects.filter(user=request.user).exists()
    except ValidationError:
        pass

    company = AccountManagerInfo.objects.all().first()
    context['company_email'] = company.email
    context['company_phone'] = company.phone


    return context
