# My Django imports
from django.urls import path, include

app_name = 'adm'

# My App imports
from trustpay_admin.views import *

# URL patterns for the trustpay_landing app
urlpatterns = [
    path('manage_cheque_deposit', ManageChequeDepositView.as_view(), name="manage_cheque_deposit"),
    path('manage_crypto_deposit', ManageCryptoDepositView.as_view(), name="manage_crypto_deposit"),
    path('manage_credit_debit', CreditDebitTransactionView.as_view(), name="manage_credit_debit"),
    path('manage_loan', ManageLoanView.as_view(), name="manage_loan"),
    path('manage_users', ManageUsersView.as_view(), name="manage_users"),
]
