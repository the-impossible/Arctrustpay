from django.shortcuts import render

# Create your views here.
# My django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal
from django.utils.decorators import method_decorator

# My app imports
from trustpay_user.models import *
from trustpay_auth.models import *
from trustpay_trx.models import *
from trustpay_user.forms import *
from trustpay_trx.forms import *
from trustpay_admin.decorators import *
from trustpay_email.mailer import *

@method_decorator([is_admin], name='dispatch')
class ManageChequeDepositView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/admin/manage_cheque_deposit.html"

    def get(self, request):
        context = {
            'object_list':ChequeDeposit.objects.all().order_by('-timestamp')
        }
        return render(request, self.template_name, context)

    def post(self, request):

        try:
            cheque_id = request.POST.get('cheque_id')
            cheque_deposit = ChequeDeposit.objects.get(id=cheque_id)

            with transaction.atomic():

                if 'approve' in request.POST:

                    completed = TransactionStatus.objects.get(transaction_status='Completed')

                    # Approve cheque
                    cheque_deposit.trx_status = completed
                    cheque_deposit.save()

                    balance, _ = Balance.objects.get_or_create(user=cheque_deposit.user)

                    amount = Decimal(cheque_deposit.amount)
                    balance.amount = balance.decimal_amount + amount

                    balance.save()

                    messages.success(request, 'Cheque deposit has been approved, respective account will be credited.')

                    user_details = {
                        'email':cheque_deposit.user.email,
                        'user':cheque_deposit.user.personal_info,
                        'amount': cheque_deposit.amount,
                        'account_number':cheque_deposit.user.username,
                        'description': cheque_deposit.transaction.description,
                        'date': cheque_deposit.timestamp,
                    }

                    Email.send(user_details, 'approve_cheque_deposit')

                elif 'disapprove' in request.POST:

                    failed = TransactionStatus.objects.get(transaction_status='Failed')

                    # Approve cheque
                    cheque_deposit.trx_status = failed
                    cheque_deposit.save()

                    messages.success(request, 'Cheque deposit has been disapproved.')

                    user_details = {
                        'email':cheque_deposit.user.email,
                        'user':cheque_deposit.user.personal_info,
                        'amount': cheque_deposit.amount,
                        'account_number':cheque_deposit.user.username,
                        'description': cheque_deposit.transaction.description,
                        'date': cheque_deposit.timestamp,
                    }

                    Email.send(user_details, 'disapprove_cheque_deposit')

                return redirect('adm:manage_cheque_deposit')

        except (ChequeDeposit.DoesNotExist, TransactionStatus.DoesNotExist):
            context = {
                'object_list':ChequeDeposit.objects.all().order_by('-timestamp')
            }
            messages.error(request, 'There was an error with your submission. Please try again.')
            return render(request, self.template_name, context)

@method_decorator([is_admin], name='dispatch')
class ManageCryptoDepositView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/admin/manage_crypto_deposit.html"

    def get(self, request):
        context = {
            'object_list':CryptoDeposit.objects.all().order_by('-timestamp')
        }
        return render(request, self.template_name, context)

    def post(self, request):

        try:
            crypto_id = request.POST.get('crypto_id')
            crypto_deposit = CryptoDeposit.objects.get(id=crypto_id)

            with transaction.atomic():

                if 'approve' in request.POST:

                    completed = TransactionStatus.objects.get(transaction_status='Completed')

                    # Approve crypto
                    crypto_deposit.trx_status = completed
                    crypto_deposit.save()

                    balance, _ = Balance.objects.get_or_create(user=crypto_deposit.user)

                    amount = Decimal(crypto_deposit.amount)
                    balance.amount = balance.decimal_amount + amount

                    balance.save()
                    messages.success(request, 'Crypto deposit has been approved, respective account will be credited.')

                    user_details = {
                        'email':crypto_deposit.user.email,
                        'user':crypto_deposit.user.personal_info,
                        'crypto_amount': crypto_deposit.amount,
                        'crypto_type':crypto_deposit.crypto_type.crypto_network,
                        'wallet_address': crypto_deposit.crypto_type.crypto_address,
                        'date': crypto_deposit.timestamp,
                    }

                    Email.send(user_details, 'approve_crypto_deposit')

                elif 'disapprove' in request.POST:

                    failed = TransactionStatus.objects.get(transaction_status='Failed')

                    # DisApprove crypto deposit
                    crypto_deposit.trx_status = failed
                    crypto_deposit.save()

                    messages.success(request, 'Crypto deposit has been disapproved.')

                    user_details = {
                        'email':crypto_deposit.user.email,
                        'user':crypto_deposit.user.personal_info,
                        'crypto_amount': crypto_deposit.amount,
                        'crypto_type':crypto_deposit.crypto_type.crypto_network,
                        'wallet_address': crypto_deposit.crypto_type.crypto_address,
                        'date': crypto_deposit.timestamp,
                    }

                    Email.send(user_details, 'disapprove_crypto_deposit')

                return redirect('adm:manage_crypto_deposit')

        except (CryptoDeposit.DoesNotExist, TransactionStatus.DoesNotExist):

            context = {
                'object_list':CryptoDeposit.objects.all().order_by('-timestamp')
            }

            messages.error(request, 'There was an error with your submission. Please try again.')
            return render(request, self.template_name, context)

@method_decorator([is_admin], name='dispatch')
class CreditDebitTransactionView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/admin/credit_debit.html"

    def get(self, request):

        context = {
            'object_list' : Transaction.objects.all().order_by('-timestamp')
        }
        return render(request, self.template_name, context)

    def post(self, request):

        try:
            trx_id = request.POST.get('trx_id')
            trx = Transaction.objects.select_related('cheque_trx', 'crypto_trx', 'withdraw_trx', 'f_wire_trx', 'd_wire_trx', 'transfer_trx',).get(id=trx_id)

            with transaction.atomic():

                if 'disapprove' in request.POST:

                    failed = TransactionStatus.objects.get(transaction_status='Failed')
                    method = TransactionMethod.objects.get(method='Other')

                    trf_type = TransferType.objects.filter(transfer_type=str(trx.get_origin())).first()

                    if trf_type not in ['cheque_trx', 'crypto_trx']:
                        fee_obj = TransactionCharges.objects.filter(trf_type=trf_type).first()
                        fee = fee_obj.charges if fee_obj else 0

                    # DisApprove trx
                    trx.trx_status = failed
                    trx.save()

                    completed = TransactionStatus.objects.get(transaction_status='Completed')
                    transaction_type = TransactionType.objects.filter(transaction_type='Credit').first()

                    related_fields = [
                        'cheque_trx', 'crypto_trx', 'withdraw_trx',
                        'f_wire_trx', 'd_wire_trx', 'transfer_trx'
                    ]

                    related_model = None

                    for field in related_fields:
                        if hasattr(trx, field):
                            related_model = getattr(trx, field)
                            break

                    if related_model:
                        related_model.trx_status = failed
                        related_model.save()

                    new_trx = Transaction(
                        user=trx.user,
                        transaction_type=transaction_type,
                        transaction_method=trx.transaction_method,
                        trx_status=completed,
                        amount=trx.amount,
                        description=f"${trx.amount} Reversal for {trx.trx_reference} Transaction",
                    )

                    if trf_type not in ['cheque_trx', 'crypto_trx']:

                        charges_trx = Transaction(
                            user=trx.user,
                            transaction_type=transaction_type,
                            transaction_method=trx.transaction_method,
                            trx_status=completed,
                            amount=fee,
                            description=f"${fee} Charges Reversal for {trx.trx_reference} Transaction",
                        )
                        charges_trx.save(reversal=True)

                    new_trx.save(reversal=True)

                    balance, _ = Balance.objects.get_or_create(user=trx.user)

                    total = Decimal(trx.amount) + Decimal(fee)
                    balance.amount = balance.decimal_amount + total

                    balance.save()
                    messages.success(request, 'Transaction has been disapproved, respective account will be credited.')

                    # SEND MAIL

                elif 'approve' in request.POST:

                    completed = TransactionStatus.objects.get(transaction_status='Completed')

                    # Approve trx
                    trx.trx_status = completed
                    trx.save()

                    related_fields = [
                        'cheque_trx', 'crypto_trx', 'withdraw_trx',
                        'f_wire_trx', 'd_wire_trx', 'transfer_trx'
                    ]

                    related_model = None

                    for field in related_fields:
                        if hasattr(trx, field):
                            related_model = getattr(trx, field)
                            break

                    if related_model:
                        related_model.trx_status = completed
                        related_model.save()

                    messages.success(request, 'Transaction has been approved.')

                return redirect('adm:manage_credit_debit')

        except (Transaction.DoesNotExist, TransactionStatus.DoesNotExist):

            context = {
                'object_list':Transaction.objects.all().order_by('-timestamp')
            }

            messages.error(request, 'There was an error with your submission. Please try again.')
            return render(request, self.template_name, context)

@method_decorator([is_admin], name='dispatch')
class ManageLoanView(LoginRequiredMixin, View, SuccessMessageMixin):

    template_name = "backend/admin/manage_loan.html"

    def get(self, request):

        context = {
            'object_list':MortgageApplication.objects.filter(mortgage_application__isnull=False).order_by('-timestamp'),
        }

        return render(request, self.template_name, context)

    def post(self, request):

        try:
            mortgage_id = request.POST.get('mortgage_id')
            mortgage = MortgageApplication.objects.get(id=mortgage_id)

            with transaction.atomic():

                if 'disapprove' in request.POST:

                    failed = TransactionStatus.objects.get(transaction_status='Failed')

                    # Approve mortgage
                    mortgage.status = failed
                    mortgage.save()
                    messages.success(request, 'Morgage has been disapproved.')

                    # SEND USER MAIL

                elif 'approve' in request.POST:

                    completed = TransactionStatus.objects.get(transaction_status='Completed')

                    # Approve mortgage
                    mortgage.status = completed
                    mortgage.save()

                    messages.success(request, 'Morgage Application has been approved.')

                    # SEND USER MAIL

                elif 'approve_deposit' in request.POST:

                    deposit = MortgageDeposit.objects.get(application=mortgage)

                    # Approve Deposit
                    deposit.approved = True
                    deposit.save()

                    messages.success(request, 'Morgage Deposit has been approved.')

                    # SEND USER MAIL

                return redirect('adm:manage_loan')

        except (MortgageApplication.DoesNotExist, MortgageDeposit.DoesNotExist):

            messages.error(request, 'There was an error with your request. Please try again.')
            return redirect('adm:manage_loan')

@method_decorator([is_admin], name='dispatch')
class ManageUsersView(LoginRequiredMixin, View, SuccessMessageMixin):

    template_name = "backend/admin/manage_users.html"

    def get(self, request):

        context = {
            'object_list':User.objects.filter(is_staff=False).order_by('-date_joined'),
        }

        return render(request, self.template_name, context)

    def post(self, request):

        user_id = request.POST['user_id']
        balance_amount = request.POST['balance_amount']

        try:

            user = User.objects.filter(user_id=user_id).first()

            user_balance = Balance.objects.filter(user=user).first()
            current_balance = Decimal(user_balance.amount)
            topup_balance = Decimal(balance_amount)

            total_balance = current_balance + topup_balance

            user_balance.amount = total_balance
            user_balance.save()

            messages.success(request, 'Balance has been updated')
            return redirect('adm:manage_users')

        except (User.DoesNotExist):
            messages.error(request, 'Failed to get user, Try again.')


        context = {
            'object_list':User.objects.filter(is_staff=False).order_by('-date_joined'),
        }

        return render(request, self.template_name, context)

