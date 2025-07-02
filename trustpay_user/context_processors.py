from django.conf import settings
from django.core.exceptions import ValidationError
from trustpay_user.models import *

def global_context(request):

    context = {}

    context['support_details'] = AccountManagerInfo.objects.all().first()

    return context
