# Django imports
from django.contrib import admin

# My app imports
from trustpay_trx.models import *

# Register your models here.
admin.site.register(TransactionType)
admin.site.register(TransactionStatus)
admin.site.register(TransactionMethod)
admin.site.register(CryptoWalletDetail)
admin.site.register(Balance)
admin.site.register(Transaction)
admin.site.register(ACHTransfer)
admin.site.register(CryptoDeposit)
admin.site.register(ChequeDeposit)
admin.site.register(TransactionCharges)
admin.site.register(TransferType)
admin.site.register(IMFCode)
admin.site.register(DomesticWire)
admin.site.register(InternationalWire)
admin.site.register(MortgageApplication)
admin.site.register(EmploymentAndPropertyAppraisal)
admin.site.register(MortgageDeposit)