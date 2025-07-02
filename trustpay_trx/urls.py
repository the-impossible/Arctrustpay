# My Django imports
from django.urls import path, include

app_name = 'trx'

# My App imports
from trustpay_trx.views import *

# URL patterns for the trustpay_users app
urlpatterns = [
    path('crypto_deposit', CryptoDepositView.as_view(), name="crypto_deposit"),
    path('complete_crypto_deposit', CompleteCryptoDepositView.as_view(), name="complete_crypto_deposit"),

    path('cheque_deposit', ChequeDepositView.as_view(), name="cheque_deposit"),

    path('internal_transfer', InternalTransferView.as_view(), name="internal_transfer"),
    path('validate_recipient_account/', validate_recipient_account, name="validate_recipient_account"),
    path('confirm_internal_transfer', ConfirmInternalTransferView.as_view(), name="confirm_internal_transfer"),

    path('ach_transfer', ACHTransferView.as_view(), name="ach_transfer"),
    path('confirm_ach_transfer', ConfirmACHTransferView.as_view(), name="confirm_ach_transfer"),

    path('d_wire_transfer', DomesticWireView.as_view(), name="d_wire_transfer"),
    path('confirm_d_wire_transfer', ConfirmDomesticWireView.as_view(), name="confirm_d_wire_transfer"),

    path('f_wire_transfer', InternationalWireView.as_view(), name="f_wire_transfer"),
    path('confirm_f_wire_transfer', ConfirmInternationalWireView.as_view(), name="confirm_f_wire_transfer"),

    path('credit_debit_transaction', CreditDebitTransactionView.as_view(), name="credit_debit_transaction"),

    path('take_loan', TakeLoanView.as_view(), name="take_loan"),
    path('repay_loan', RepayLoanView.as_view(), name="repay_loan"),

    path('transactions', TransactionPageView.as_view(), name="transactions"),
]