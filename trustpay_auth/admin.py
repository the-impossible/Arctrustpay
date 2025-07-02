from django.contrib import admin
from trustpay_auth.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(EmailSendCount)

