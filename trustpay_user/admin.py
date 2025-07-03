from django.contrib import admin
from trustpay_user.models import *

# Register your models here.
admin.site.register(Gender)
admin.site.register(AccountType)
admin.site.register(RelationshipStatus)
admin.site.register(EmploymentStatus)
admin.site.register(PersonalInfo)
admin.site.register(ContactInfo)
admin.site.register(BankAccountInfo)
admin.site.register(AccountManagerInfo)