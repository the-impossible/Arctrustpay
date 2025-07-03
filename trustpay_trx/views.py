# My django imports
from django.shortcuts import render, redirect
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
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator

# My app imports
from trustpay_user.models import *
from trustpay_trx.models import *
from trustpay_user.forms import *
from trustpay_trx.forms import *
from trustpay_trx.decorators import *
from trustpay_user.decorators import *
from trustpay_email.mailer import *



# Create your views here.
@method_decorator([has_updated], name='dispatch')
class CryptoDepositView(LoginRequiredMixin, TemplateView, SuccessMessageMixin):
    template_name = "backend/crypto/deposit.html"
    form = DepositEnquiryForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['object_list'] = CryptoDeposit.objects.all().order_by('-timestamp')
        return context

@method_decorator([has_updated], name='dispatch')
class CompleteCryptoDepositView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/crypto/complete_deposit.html"
    form = CompleteDepositEnquiryForm

    def post(self, request):
        form = self.form(request.POST)

        if 'crypto_deposit' in request.POST:
            deposit_amount = request.POST.get('deposit_amount')
            payment_method = request.POST.get('payment_method')

            wallet_details = CryptoWalletDetail.objects.filter(pk=payment_method).first()

            context = {
                'form': self.form,
                'wallet_address': wallet_details,
                'deposit_amount': deposit_amount,
            }

            return render(request, self.template_name, context)

        elif 'complete_payment' in request.POST:

            form = self.form(request.POST, request.FILES)
            wallet = request.POST.get('wallet')
            deposit_amount = request.POST.get('deposit_amount')
            crypto_type = CryptoWalletDetail.objects.filter(pk=wallet).first()

            if form.is_valid():

                payment_proof = form.cleaned_data.get('payment_proof')

                with transaction.atomic():

                    crypto = CryptoDeposit.objects.create(user=request.user, crypto_type=crypto_type, amount=deposit_amount, transaction_image=payment_proof)

                    user_details = {
                        'email':crypto.user.email,
                        'user':crypto.user.personal_info,
                        'crypto_amount': crypto.amount,
                        'crypto_type':crypto.crypto_type.crypto_network,
                        'wallet_address': crypto.crypto_type.crypto_address,
                        'date': crypto.timestamp,
                    }

                    Email.send(user_details, 'crypto_deposit_processing')
                    Email.send(user_details, 'admin_crypto_deposit_processing')

                messages.success(request, 'Our team will verify your payment. Once confirmed, your account will be credited.')

                return redirect('trx:crypto_deposit')
            else:
                messages.error(request, 'There was an error with your submission. Please try again.')
                context = {
                    'form': form,
                    'wallet_address': wallet_details,
                    'deposit_amount': deposit_amount,
                }
                return render(request, self.template_name, context)
        else:
            messages.error(request, "Couldn't handle request, Try again!")

            return render(request, self.template_name, context)

@method_decorator([has_updated], name='dispatch')
class ChequeDepositView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/cheque/cheque_deposit.html"
    form = ChequeDepositForm

    def get(self, request):
        context = {
            'form':self.form,
            'object_list':ChequeDeposit.objects.all().order_by('-timestamp')
        }
        return render(request, self.template_name, context)

    def post(self, request):

        form = self.form(request.POST, request.FILES)

        if form.is_valid():

            deposit_amount = request.POST.get('deposit_amount')
            front_of_cheque = form.cleaned_data.get('front_of_cheque')
            back_of_cheque = form.cleaned_data.get('back_of_cheque')

            with transaction.atomic():
                chq = ChequeDeposit.objects.create(user=request.user, amount=deposit_amount, cheque_front_img=front_of_cheque, cheque_back_img=back_of_cheque)

                user_details = {
                    'email':chq.user.email,
                    'user':chq.user.personal_info,
                    'amount': chq.amount,
                    'account_number':chq.user.username,
                    'description': chq.transaction.description,
                    'date': chq.timestamp,
                }

                Email.send(user_details, 'cheque_deposit_processing')

                Email.send(user_details, 'admin_cheque_deposit_processing')


            messages.success(request, 'Our team will verify your payment. Once confirmed, your account will be credited.')

            return redirect('trx:cheque_deposit')

        else:
            messages.error(request, 'There was an error with your submission. Please try again.')
            context = {
                'form': form,
                'object_list':ChequeDeposit.objects.all().order_by('-timestamp')
            }
            return render(request, self.template_name, context)

@method_decorator([has_updated], name='dispatch')
class InternalTransferView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/transfer/internal_transfer.html"
    form = InternalTransferForm

    def get(self, request):

        trx_method = TransactionMethod.objects.filter(method='Internal Transfer').first()

        context = {
            'form':self.form,
            'object_list' : Transaction.objects.filter(user=self.request.user, transaction_method=trx_method).order_by('-timestamp')
        }
        return render(request, self.template_name, context)

    def post(self, request):

        form = self.form(request.POST)

        if form.is_valid():
            recipient_account = request.POST.get('recipient_account')

            try:
                recipient = User.objects.get(username=recipient_account)
                sender = User.objects.get(username=request.user.username)


                trf_type = TransferType.objects.filter(transfer_type="Internal Transfer").first()
                fee = TransactionCharges.objects.filter(trf_type=trf_type).first().charges
                amount = form.cleaned_data.get('amount')

                context = {
                    'sender_account':str(sender.username),
                    'sender_name':str(sender.personal_info),
                    'recipient_account':str(recipient.username),
                    'recipient_name':str(recipient.personal_info),
                    'fee':str(fee),
                    'description':str(form.cleaned_data.get('description')),
                    'amount':str(amount),
                }

                request.session['transfer_data'] = context

                return redirect('trx:confirm_internal_transfer')

            except User.DoesNotExist:

                messages.error(request, "Couldn't valid recipient account, Try Again!!")

                context = {
                    'form':form,
                }

                return render(request, self.template_name, context)

        else:

            messages.error(request, 'There was an error with your submission. Please try again.')
            context = {
                'form': form,
            }
            return render(request, self.template_name, context)

@method_decorator([has_updated, has_transaction_pin, has_transfer_data], name='dispatch')
class ConfirmInternalTransferView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/transfer/confirm_internal_transfer.html"

    def get(self, request):

        context = {

            'transfer_data':request.session.get('transfer_data'),
        }

        return render(request, self.template_name, context)

    def post(self, request):

        transfer_data = request.session.get('transfer_data')
        transaction_pin = request.POST['transaction_pin']

        # Get sender balance and verify if transaction is posible
        sender_balance = Balance.objects.filter(user=request.user).first().amount

        total_amount = Decimal(transfer_data['amount']) + Decimal(transfer_data['fee'])

        if sender_balance >= total_amount:

            # Check if transaction_pin is valid
            storePin = TransactionPin.objects.get(user=request.user)
            if check_password(transaction_pin, storePin.pin):
                with transaction.atomic():

                    try:
                        # Transaction type
                        trx_types = TransactionType.objects.all()
                        transaction_types = {trx_type.transaction_type.lower():trx_type for trx_type in trx_types}
                        credit_type = transaction_types['credit']
                        debit_type = transaction_types['debit']
                        # Transaction method
                        trx_method = TransactionMethod.objects.filter(method='Internal Transfer').first()
                        trx_status = TransactionStatus.objects.filter(transaction_status='Completed').first()
                        # Receiver
                        receiver = User.objects.get(username=transfer_data['recipient_account'])

                        # Debit SENDER
                        trx = Transaction.objects.create(
                            user=request.user,
                            transaction_type=debit_type,
                            transaction_method=trx_method,
                            trx_status=trx_status,
                            amount=str(transfer_data['amount']),
                            description=transfer_data['description']
                        )

                        # Credit RECIEVER
                        Transaction.objects.create(
                            user=receiver,
                            transaction_type=credit_type,
                            transaction_method=trx_method,
                            trx_status=trx_status,
                            amount=str(transfer_data['amount']),
                            description=transfer_data['description']
                        )

                        user_details = {
                            'sender_email':request.user.email,
                            'receiver_email':receiver.email,
                            'sender_name':request.user.personal_info,
                            'sender_account':request.user.username,
                            'method': trx_method.method,
                            'recipient_account':receiver.username,
                            'recipient_name':receiver.personal_info,
                            'amount':str(transfer_data['amount']),
                            'description':transfer_data['description'],
                            'date': trx.timestamp,
                        }

                        Email.send(user_details, 'sender_internal_trf')
                        Email.send(user_details, 'receiver_internal_trf')

                        del request.session['transfer_data']

                        messages.success(request, 'Transaction Successful ')
                        return redirect('trx:internal_transfer')
                    except User.DoesNotExist:
                        messages.error(request, 'Invalid account number!! ')
                        return redirect('trx:internal_transfer')

            else:

                messages.error(request, 'Invalid transaction pin!! ')
                context = {
                    'transfer_data': transfer_data,
                }
                return render(request, self.template_name, context)
        else:
            del request.session['transfer_data']

            messages.error(request, 'Insufficient balance !! ')
            return redirect('trx:internal_transfer')

@method_decorator([has_updated], name='dispatch')
class TransactionPageView(LoginRequiredMixin, TemplateView, SuccessMessageMixin):
    template_name = "backend/trx/transaction.html"
    form = DepositEnquiryForm

def validate_recipient_account(request):

    account_number = request.GET.get("recipient_account")
    context = {}

    if int(len(account_number)) < 10:
        context["recipient_name"] = ""
        context["valid"] = False

    elif int(len(account_number)) > 10:
        context["recipient_name"] = ""
        context["valid"] = False
    else:
        try:
            user = User.objects.get(username=account_number)
            print()

            if user != request.user:

                if user.personal_info.first_name == None:
                    context["recipient_name"] = "Invalid account"
                    context["valid"] = False
                else:
                    context["recipient_name"] = user.personal_info
                    context["valid"] = True

            else:
                context["recipient_name"] = "Invalid account"
                context["valid"] = False

        except User.DoesNotExist:
            context["recipient_name"] = "Invalid account"
            context["valid"] = False

    html = render_to_string("backend/transfer/partials/recipient_name.html", context)
    return HttpResponse(html)

@method_decorator([has_updated], name='dispatch')
class ACHTransferView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/transfer/ach_transfer.html"
    form = ACHTransferForm

    def get(self, request):

        context = {
            'form':self.form,
            'object_list' : ACHTransfer.objects.filter(user=self.request.user).order_by('-timestamp')
        }
        return render(request, self.template_name, context)

    def post(self, request):

        form = self.form(request.POST)

        if form.is_valid():

            trf_type = TransferType.objects.filter(transfer_type="ACH Transfer").first()
            fee = TransactionCharges.objects.filter(trf_type=trf_type).first().charges
            amount = form.cleaned_data.get('amount')

            sender_balance = Balance.objects.filter(user=request.user).first().amount
            total_amount = Decimal(amount) + Decimal(fee)

            account_name = form.cleaned_data.get('account_name')
            account_number = form.cleaned_data.get('account_number')
            routing_number = form.cleaned_data.get('routing_number')
            account_type = form.cleaned_data.get('account_type')
            note = form.cleaned_data.get('note')

            context = {
                'fee':str(fee),
                'amount':str(amount),
                'account_name':str(account_name),
                'account_number':str(account_number),
                'routing_number':str(routing_number),
                'account_type':str(account_type),
                'note':str(note),
                'total': str(total_amount),
            }

            request.session['ach_data'] = context
            return redirect('trx:confirm_ach_transfer')

        else:

            messages.error(request, 'There was an error with your submission. Please try again.')
            context = {
                'form': form,
            }
            return render(request, self.template_name, context)

@method_decorator([has_updated, has_transaction_pin, has_ach_data], name='dispatch')
class ConfirmACHTransferView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/transfer/confirm_ach_transfer.html"

    def get(self, request):

        context = {

            'ach_data':request.session.get('ach_data'),
        }

        return render(request, self.template_name, context)

    def post(self, request):

        ach_data = request.session.get('ach_data')
        transaction_pin = request.POST['transaction_pin']
        imfCode = request.POST['imfCode']

        # Get sender balance and verify if transaction is posible
        sender_balance = Balance.objects.filter(user=request.user).first().amount
        total_amount = Decimal(ach_data['amount']) + Decimal(ach_data['fee'])

        if sender_balance >= total_amount:

            # Check if transaction_pin is valid
            storePin = TransactionPin.objects.get(user=request.user)
            storeimfCode,_ = IMFCode.objects.get_or_create(user=request.user)

            code_valid = (storeimfCode.code == imfCode)

            tPin_valid = check_password(transaction_pin, storePin.pin)

            if tPin_valid and code_valid:

                with transaction.atomic():

                    # Transaction type
                    trx_types = TransactionType.objects.all()
                    transaction_types = {trx_type.transaction_type.lower():trx_type for trx_type in trx_types}
                    debit_type = transaction_types['debit']

                    # Transaction method
                    trx_method = TransactionMethod.objects.filter(method='Bank Transfer').first()
                    acct_type = AccountType.objects.filter(account_type=ach_data['account_type']).first()

                    # Create ACH Transfer Record
                    ach = ACHTransfer.objects.create(
                        user=request.user,
                        account_name=ach_data['account_name'],
                        account_number=ach_data['account_number'],
                        routing_number=ach_data['routing_number'],
                        account_type=acct_type,
                        amount=str(ach_data['amount']),
                        note=str(ach_data['note']),
                    )

                    user_details = {
                        'sender_name':request.user.personal_info,
                        'sender_email':request.user.email,
                        'amount':str(ach_data['amount']),
                        'date': ach.timestamp,
                        'sender_account':request.user.username,
                        'recipient_name':ach_data['account_name'],
                        'routing_number':ach_data['routing_number'],
                        'recipient_account':ach_data['account_number'],
                        'description':ach_data['note'],
                    }

                    Email.send(user_details, 'ach_transfer')

                    del request.session['ach_data']

                    messages.success(request, 'Transaction Successful')
                    return redirect('trx:ach_transfer')

            else:

                if not tPin_valid:
                    messages.error(request, 'Invalid transaction pin!! ')
                if not code_valid:
                    messages.error(request, 'Invalid IMF code!! ')
                context = {
                    'ach_data': ach_data,
                }
                return render(request, self.template_name, context)
        else:

            del request.session['ach_data']

            messages.error(request, 'Insufficient balance !! ')
            return redirect('trx:ach_transfer')

@method_decorator([has_updated], name='dispatch')
class DomesticWireView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/transfer/d_wire_transfer.html"
    form = DomesticWireForm

    def get(self, request):

        context = {
            'form':self.form,
            'object_list' : DomesticWire.objects.filter(user=self.request.user).order_by('-timestamp')
        }
        return render(request, self.template_name, context)

    def post(self, request):

        form = self.form(request.POST)

        if form.is_valid():

            trf_type = TransferType.objects.filter(transfer_type="Domestic Wire").first()
            fee = TransactionCharges.objects.filter(trf_type=trf_type).first().charges
            amount = form.cleaned_data.get('amount')

            sender_balance = Balance.objects.filter(user=request.user).first().amount
            total_amount = Decimal(amount) + Decimal(fee)

            account_name = form.cleaned_data.get('account_name')
            account_number = form.cleaned_data.get('account_number')
            bank_name = form.cleaned_data.get('bank_name')
            routing_number = form.cleaned_data.get('routing_number')
            note = form.cleaned_data.get('note')

            context = {
                'fee':str(fee),
                'amount':str(amount),
                'account_name':str(account_name),
                'account_number':str(account_number),
                'routing_number':str(routing_number),
                'bank_name':str(bank_name),
                'note':str(note),
                'total':str(total_amount),
            }

            request.session['d_wire_data'] = context
            return redirect('trx:confirm_d_wire_transfer')

        else:

            messages.error(request, 'There was an error with your submission. Please try again.')
            context = {
                'form': form,
            }
            return render(request, self.template_name, context)

@method_decorator([has_updated, has_transaction_pin, has_domestic_data], name='dispatch')
class ConfirmDomesticWireView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/transfer/confirm_d_wire_transfer.html"

    def get(self, request):

        context = {
            'd_wire_data':request.session.get('d_wire_data'),
        }

        return render(request, self.template_name, context)

    def post(self, request):

        d_wire_data = request.session.get('d_wire_data')
        transaction_pin = request.POST['transaction_pin']
        imfCode = request.POST['imfCode']

        # Get sender balance and verify if transaction is posible
        sender_balance = Balance.objects.filter(user=request.user).first()
        total_amount = Decimal(d_wire_data['amount']) + Decimal(d_wire_data['fee'])

        if sender_balance.amount >= total_amount:

            # Check if transaction_pin is valid
            storePin = TransactionPin.objects.get(user=request.user)
            storeimfCode,_ = IMFCode.objects.get_or_create(user=request.user)

            code_valid = (storeimfCode.code == imfCode)

            tPin_valid = check_password(transaction_pin, storePin.pin)

            if tPin_valid and code_valid:

                with transaction.atomic():

                    # Transaction type
                    trx_types = TransactionType.objects.all()
                    transaction_types = {trx_type.transaction_type.lower():trx_type for trx_type in trx_types}
                    debit_type = transaction_types['debit']
                    # Transaction method
                    trx_method = TransactionMethod.objects.filter(method='Bank Transfer').first()
                    bank_name = AllBank.objects.filter(bank_name=d_wire_data['bank_name']).first()

                    # Create ACH Transfer Record
                    dw = DomesticWire.objects.create(
                        user=request.user,
                        account_name=d_wire_data['account_name'],
                        account_number=d_wire_data['account_number'],
                        routing_number=d_wire_data['routing_number'],
                        bank_name=bank_name,
                        amount=str(d_wire_data['amount']),
                        note=str(d_wire_data['note']),
                    )

                    user_details = {
                        'sender_account':request.user.username,
                        'sender_email':request.user.email,
                        'sender_name':request.user.personal_info,
                        'amount':str(d_wire_data['amount']),
                        'description':d_wire_data['note'],
                        'recipient_account':str(d_wire_data['account_number']),
                        'recipient_name':str(d_wire_data['account_name']),
                        'routing_number':d_wire_data['routing_number'],
                        'date': dw.timestamp,
                        'bank_name':d_wire_data['bank_name'],
                    }

                    Email.send(user_details, 'd_wire_transfer')

                    del request.session['d_wire_data']

                    messages.success(request, 'Transaction Successful')
                    return redirect('trx:d_wire_transfer')

            else:

                if not tPin_valid:
                    messages.error(request, 'Invalid transaction pin!! ')
                if not code_valid:
                    messages.error(request, 'Invalid IMF code!! ')
                context = {
                    'd_wire_data': d_wire_data,
                }
                return render(request, self.template_name, context)
        else:

            del request.session['d_wire_data']

            messages.error(request, 'Insufficient balance !! ')
            return redirect('trx:d_wire_transfer')

@method_decorator([has_updated], name='dispatch')
class InternationalWireView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/transfer/f_wire_transfer.html"
    form = InternationalWireForm

    def get(self, request):

        context = {
            'form':self.form,
            'object_list' : InternationalWire.objects.filter(user=self.request.user).order_by('-timestamp')
        }
        return render(request, self.template_name, context)

    def post(self, request):

        form = self.form(request.POST)

        if form.is_valid():

            trf_type = TransferType.objects.filter(transfer_type="International Wire").first()
            fee = TransactionCharges.objects.filter(trf_type=trf_type).first().charges
            amount = form.cleaned_data.get('amount')

            sender_balance = Balance.objects.filter(user=request.user).first().amount
            total_amount = Decimal(amount) + Decimal(fee)

            account_name = form.cleaned_data.get('account_name')
            account_number = form.cleaned_data.get('account_number')
            bank_name = form.cleaned_data.get('bank_name')
            swift_bic_code = form.cleaned_data.get('swift_bic_code')
            bank_address = form.cleaned_data.get('bank_address')
            iban = form.cleaned_data.get('iban')
            country = request.POST['country']
            note = form.cleaned_data.get('note')

            context = {
                'fee':str(fee),
                'amount':str(amount),
                'account_name':str(account_name),
                'account_number':str(account_number),
                'swift_bic_code':str(swift_bic_code),
                'bank_name':str(bank_name),
                'bank_address':str(bank_address),
                'iban':str(iban),
                'country':str(country),
                'note':str(note),
                'total':str(total_amount),
            }

            request.session['f_wire_data'] = context
            return redirect('trx:confirm_f_wire_transfer')

        else:

            messages.error(request, 'There was an error with your submission. Please try again.')
            context = {
                'form': form,
            }
            return render(request, self.template_name, context)

@method_decorator([has_updated, has_transaction_pin, has_international_data], name='dispatch')
class ConfirmInternationalWireView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/transfer/confirm_f_wire_transfer.html"

    def get(self, request):

        context = {
            'f_wire_data':request.session.get('f_wire_data'),
        }

        return render(request, self.template_name, context)

    def post(self, request):

        f_wire_data = request.session.get('f_wire_data')
        transaction_pin = request.POST['transaction_pin']
        imfCode = request.POST['imfCode']

        # Get sender balance and verify if transaction is posible
        sender_balance = Balance.objects.filter(user=request.user).first()
        total_amount = Decimal(f_wire_data['amount']) + Decimal(f_wire_data['fee'])

        if sender_balance.amount >= total_amount:

            # Check if transaction_pin is valid
            storePin = TransactionPin.objects.get(user=request.user)
            storeimfCode,_ = IMFCode.objects.get_or_create(user=request.user)

            code_valid = (storeimfCode.code == imfCode)

            tPin_valid = check_password(transaction_pin, storePin.pin)

            if tPin_valid and code_valid:

                with transaction.atomic():

                    # Transaction type
                    trx_types = TransactionType.objects.all()
                    transaction_types = {trx_type.transaction_type.lower():trx_type for trx_type in trx_types}
                    debit_type = transaction_types['debit']
                    # Transaction method
                    trx_method = TransactionMethod.objects.filter(method='Bank Transfer').first()

                    # Create Innternation Wire Transfer Record
                    fw = InternationalWire.objects.create(
                        user=request.user,
                        account_name=f_wire_data['account_name'],
                        account_number=f_wire_data['account_number'],
                        bank_address=f_wire_data['bank_address'],
                        bank_name=f_wire_data['bank_name'],
                        swift_bic_code=f_wire_data['swift_bic_code'],
                        iban=f_wire_data['iban'],
                        country=f_wire_data['country'],
                        amount=str(f_wire_data['amount']),
                        note=str(f_wire_data['note']),
                    )

                    user_details = {
                        'sender_account':request.user.username,
                        'sender_email':request.user.email,
                        'sender_name':request.user.personal_info,
                        'amount':str(f_wire_data['amount']),
                        'description':f_wire_data['note'],
                        'recipient_account':str(f_wire_data['account_number']),
                        'recipient_name':str(f_wire_data['account_name']),
                        'swift_bic_code':f_wire_data['swift_bic_code'],
                        'bank_name':f_wire_data['bank_name'],
                        'iban':f_wire_data['iban'],
                        'date': fw.timestamp,
                    }

                    Email.send(user_details, 'f_wire_transfer')

                    del request.session['f_wire_data']

                    messages.success(request, 'Transaction Successful')
                    return redirect('trx:f_wire_transfer')

            else:

                if not tPin_valid:
                    messages.error(request, 'Invalid transaction pin!! ')
                if not code_valid:
                    messages.error(request, 'Invalid IMF code!! ')
                context = {
                    'f_wire_data': f_wire_data,
                }
                return render(request, self.template_name, context)
        else:

            del request.session['f_wire_data']

            messages.error(request, 'Insufficient balance !! ')
            return redirect('trx:f_wire_transfer')

@method_decorator([has_updated], name='dispatch')
class CreditDebitTransactionView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/trx/credit_debit.html"

    def get(self, request):

        context = {
            'object_list' : Transaction.objects.filter(user=self.request.user).order_by('-timestamp')
        }
        return render(request, self.template_name, context)

@method_decorator([has_updated], name='dispatch')
class TakeLoanView(LoginRequiredMixin, View, SuccessMessageMixin):
    template_name = "backend/loan/take_loan.html"
    form1 = MortgageApplicationForm
    form2 = EmploymentAndPropertyAppraisalForm
    form3 = MortgateDepositForm

    def get(self, request):
        step1 = MortgageApplication.objects.filter(user=request.user)

        if step1.exists():

            step2 = EmploymentAndPropertyAppraisal.objects.filter(application=step1.first())

            if step2.exists():

                if step1.first().status.transaction_status == 'Completed':

                    step3 = MortgageDeposit.objects.filter(application=step1.first())

                    if step3.exists():

                        if step3.first().approved:

                            context = {
                                'step5':'step5',
                                'amount': step1.first().amount_requested,
                            }
                            return render(request, self.template_name, context)
                        else:
                            context = {
                                'step4':'step4',
                                'amount': step1.first().amount_requested,
                                'd_pending':'d_pending',
                            }
                            return render(request, self.template_name, context)
                    else:
                        context = {
                            'step3':'step3',
                            'amount': step1.first().amount_requested,
                            'form3':self.form3,
                        }
                        return render(request, self.template_name, context)

                elif step1.first().status.transaction_status == 'Pending':
                    context = {
                        'step2':'step2',
                        'amount': step1.first().amount_requested,
                        'pending':'pending',
                    }
                    return render(request, self.template_name, context)

                elif step1.first().status.transaction_status == 'Failed':
                    context = {
                        'step2':'step2',
                        'amount': step1.first().amount_requested,
                        'failed':'failed',
                    }
                    return render(request, self.template_name, context)

            else:
                context = {
                    'step1':'step1',
                    'form2':self.form2,
                }
                return render(request, self.template_name, context)

        else:

            context = {
                'step0':'step0',
                'form1':self.form1,
            }

            return render(request, self.template_name, context)

    def post(self, request):

        if 'step1' in request.POST:

            form1 = self.form1(request.POST, request.FILES)

            if form1.is_valid():

                instance = form1.save(commit=False)
                instance.user = request.user
                instance.save()

                messages.success(request, 'Pre-Mortgage Application successful!!')

                return redirect('trx:take_loan')

            else:
                messages.error(request, form1.errors.as_text())
                context = {
                    'step0':'step0',
                    'form1': form1,
                }
                return render(request, self.template_name, context)

        if 'step2' in request.POST:

            application = MortgageApplication.objects.filter(user=request.user).first()

            form2 = self.form2(request.POST, request.FILES)

            if form2.is_valid():

                instance = form2.save(commit=False)
                instance.application = application
                instance.save()

                messages.success(request, 'Employment and Property Appraisal successful!!')

                return redirect('trx:take_loan')

            else:

                messages.error(request, form2.errors.as_text())
                context = {
                    'step1':'step1',
                    'form2': form2,
                }
                return render(request, self.template_name, context)

        if 'step3' in request.POST:

            application = MortgageApplication.objects.filter(user=request.user).first()

            form3 = self.form3(request.POST, request.FILES)

            if form3.is_valid():

                cheque_front_img = form3.cleaned_data.get('front_of_cheque')
                cheque_back_img = form3.cleaned_data.get('back_of_cheque')

                MortgageDeposit.objects.create(
                    application=application,
                    deposit_amount=application.amount_requested,
                    cheque_front_img=cheque_front_img,
                    cheque_back_img=cheque_back_img,
                )

                messages.success(request, 'Cheque has been deposited successful!')

                return redirect('trx:take_loan')

            else:

                messages.error(request, form3.errors.as_text())
                context = {
                    'step1':'step1',
                    'amount':application.amount_requested,
                    'form3': form3,
                }
                return render(request, self.template_name, context)

        if 'restart' in request.POST:
            application = MortgageApplication.objects.filter(user=request.user).first()
            application.delete()
            messages.success(request, "You can now re-apply!")
            return redirect('trx:take_loan')

        else:

            messages.error(request, "Couldn't process request, Try again!")
            return redirect('trx:take_loan')

@method_decorator([has_updated], name='dispatch')
class RepayLoanView(LoginRequiredMixin, View, SuccessMessageMixin):

    template_name = "backend/loan/repay_loan.html"

    def get(self, request):

        context = {
            'object_list':LoanRepayment.objects.filter(application__user=request.user),
        }

        return render(request, self.template_name, context)



