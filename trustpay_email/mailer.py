# My django imports
import threading #for enhancing page functionality
from django.core.mail import send_mail #for sending mails
from django.conf import settings #to gain access to variables from the settings
from django.http import request #to gain access to the request object
from django.views import View
from django.shortcuts import redirect, render
from django.urls import reverse
from django.template.loader import get_template #used for getting html template
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from django.contrib import messages #for sending messages
from django.utils.html import strip_tags
from trustpay_user.models import *

# My App imports

class EmailThread(threading.Thread):
    def __init__(self, email_subject, email_body, receiver):
        self.email_subject = email_subject
        self.email_body = email_body
        self.sender = 'info@arctrustpay.com'
        self.receiver = receiver
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.email_subject,
            self.email_body,
            self.sender,
            self.receiver,
            html_message=self.email_body,
            fail_silently=False
        )

class AppTokenGenerator(PasswordResetTokenGenerator):
    def __make_hash_value(self, user, timestamp):
        return (text_type(user.is_active) + text_type(user.id)+text_type(timestamp))

email_activation_token = AppTokenGenerator()

class Mailer(View):

    def send_mail_directly(self, subject, body, recipient_list):
        pass
        # send_mail(
        #     subject,
        #     strip_tags(body),  # Plain text fallback body (can be left empty if using HTML only)
        #     settings.DEFAULT_FROM_EMAIL,
        #     recipient_list,
        #     html_message=body,
        #     fail_silently=False
        # )


    def send(self, user_details, which):
        welcome = f'Welcome to {settings.APP_NAME.upper()}'
        reset = f'Reset Your {settings.APP_NAME.upper()} Account Password'

        if which == 'welcome':
            activation_path = 'email/welcome.html'
            receiver = [user_details['email']]
            email_subject = welcome
            context_data = {'app_name':settings.APP_NAME, 'user': user_details['email'], 'account_number': user_details['account_number']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'reset':
            link = reverse('auth:reset-password', kwargs={'uidb64':user_details['uid'], 'token':user_details['token']})
            activation_url = settings.HTTP+user_details['domain']+link
            activation_path = 'email/reset_password.html'
            receiver = [user_details['email']]
            email_subject = reset
            context_data = {'app_name':settings.APP_NAME, 'user': user_details['fullname'], 'activate': activation_url}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'approve_cheque_deposit':
            activation_path = 'email/cheque_deposit.html'
            receiver = [user_details['email']]
            email_subject = f"Cheque Deposit Successful - ${user_details['amount'] } Received"
            context_data = {'app_name':settings.APP_NAME, 'user': user_details['user'], 'amount': user_details['amount'], 'account_number': user_details['account_number'], 'description': user_details['description'], 'date': user_details['date'],}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'cheque_deposit_processing':

            activation_path = 'email/cheque_deposit_processing.html'
            receiver = [user_details['email']]
            email_subject = f"Received Cheque Deposit in Process - ${user_details['amount'] } Under Review"
            context_data = {'app_name':settings.APP_NAME, 'user': user_details['user'], 'amount': user_details['amount'], 'account_number': user_details['account_number'], 'description': user_details['description'], 'date': user_details['date'],}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()


        elif which == 'admin_cheque_deposit_processing':

            activation_path = 'email/admin_cheque_deposit_processing.html'

            company = AccountManagerInfo.objects.all().first()
            receiver = [company.email]

            email_subject = f"New Cheque Deposit Submitted - ${user_details['amount'] } by {user_details['account_number']}"
            context_data = {'app_name':settings.APP_NAME, 'user': user_details['user'], 'amount': user_details['amount'], 'account_number': user_details['account_number'], 'description': user_details['description'], 'date': user_details['date'],}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'crypto_deposit_processing':

            activation_path = 'email/crypto_deposit_processing.html'
            receiver = [user_details['email']]
            email_subject = f"Received Cheque Deposit in Process - ${user_details['crypto_amount'] } Under Review"
            context_data = {'app_name':settings.APP_NAME, 'user': user_details['user'], 'crypto_amount': user_details['crypto_amount'], 'crypto_type': user_details['crypto_type'], 'wallet_address': user_details['wallet_address'], 'date': user_details['date']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'admin_crypto_deposit_processing':

            activation_path = 'email/admin_crypto_deposit_processing.html'
            company = AccountManagerInfo.objects.all().first()
            receiver = [company.email]

            email_subject = f"New Cheque Deposit Submitted - ${user_details['crypto_amount'] } by {user_details['user']}"
            context_data = {'app_name':settings.APP_NAME, 'user': user_details['user'], 'crypto_amount': user_details['crypto_amount'], 'crypto_type': user_details['crypto_type'], 'wallet_address': user_details['wallet_address'], 'date': user_details['date']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'disapprove_cheque_deposit':
            activation_path = 'email/cheque_deposit_failed.html'
            receiver = [user_details['email']]
            email_subject = f"Cheque Deposit Failed - Action Required"
            context_data = {'app_name':settings.APP_NAME, 'user': user_details['user'], 'amount': user_details['amount'], 'account_number': user_details['account_number'], 'description': user_details['description'], 'date': user_details['date']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'approve_crypto_deposit':
            activation_path = 'email/crypto_deposit.html'
            receiver = [user_details['email']]
            email_subject = f"Crypto Deposit Successful - ${user_details['crypto_amount']} {user_details['crypto_type']} Received"
            context_data = {'app_name':settings.APP_NAME, 'user': user_details['user'], 'crypto_amount': user_details['crypto_amount'], 'crypto_type': user_details['crypto_type'], 'wallet_address': user_details['wallet_address'], 'date': user_details['date']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'disapprove_crypto_deposit':
            activation_path = 'email/crypto_deposit_failed.html'
            receiver = [user_details['email']]
            email_subject = f"Crypto Deposit Disapproved - Action Required"
            context_data = {'app_name':settings.APP_NAME, 'user': user_details['user'], 'crypto_amount': user_details['crypto_amount'], 'crypto_type': user_details['crypto_type'], 'wallet_address': user_details['wallet_address'], 'date': user_details['date']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'request_support':
            activation_path = 'email/support_request.html'

            company = AccountManagerInfo.objects.all().first()
            receiver = [company.email]

            email_subject = f"New Support Request - from {user_details['name']}"
            context_data = {'app_name':settings.APP_NAME, 'name': user_details['name'], 'email': user_details['email'], 'subject': user_details['subject'], 'message': user_details['message']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'sender_internal_trf':

            activation_path = 'email/transfer.html'
            receiver = [user_details['sender_email']]

            email_subject = f"Transfer Completed - ${ user_details['amount'] } Sent Successfully"
            context_data = {'app_name':settings.APP_NAME, 'sender_name': user_details['sender_name'], 'method': user_details['method'], 'recipient_account': user_details['recipient_account'], 'date': user_details['date'], 'sender_account': user_details['sender_account'], 'recipient_account': user_details['recipient_account'], 'recipient_name': user_details['recipient_name'], 'amount': user_details['amount'], 'description': user_details['description']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'receiver_internal_trf':

            activation_path = 'email/transfer_receiver.html'
            receiver = [user_details['receiver_email']]

            email_subject = f"You've Received a Transfer - ${ user_details['amount'] } Credited to Your Account"
            context_data = {'app_name':settings.APP_NAME, 'sender_name': user_details['sender_name'], 'method': user_details['method'], 'recipient_account': user_details['recipient_account'], 'date': user_details['date'], 'sender_account': user_details['sender_account'], 'recipient_account': user_details['recipient_account'], 'recipient_name': user_details['recipient_name'], 'amount': user_details['amount'], 'description': user_details['description']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'ach_transfer':

            activation_path = 'email/ach_transfer.html'
            receiver = [user_details['sender_email']]

            email_subject = f"Your ACH Transfer is Being Processed - ${ user_details['amount'] }"
            context_data = {'app_name':settings.APP_NAME, 'sender_name': user_details['sender_name'], 'sender_account': user_details['sender_account'], 'routing_number': user_details['routing_number'], 'date': user_details['date'], 'sender_account': user_details['sender_account'], 'recipient_account': user_details['recipient_account'], 'recipient_name': user_details['recipient_name'], 'amount': user_details['amount'], 'description': user_details['description']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'd_wire_transfer':

            activation_path = 'email/d_wire.html'
            receiver = [user_details['sender_email']]

            email_subject = f"Domestic Wire Transfer Initiated - ${ user_details['amount'] }"
            context_data = {'app_name':settings.APP_NAME, 'sender_name': user_details['sender_name'], 'sender_account': user_details['sender_account'], 'routing_number': user_details['routing_number'], 'date': user_details['date'], 'sender_account': user_details['sender_account'], 'recipient_account': user_details['recipient_account'], 'recipient_name': user_details['recipient_name'], 'amount': user_details['amount'], 'description': user_details['description'], 'bank_name': user_details['bank_name']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'f_wire_transfer':

            activation_path = 'email/f_wire.html'
            receiver = [user_details['sender_email']]

            email_subject = f"International Wire Transfer Initiated - ${ user_details['amount'] }"
            context_data = {'app_name':settings.APP_NAME, 'sender_name': user_details['sender_name'], 'sender_account': user_details['sender_account'], 'swift_bic_code': user_details['swift_bic_code'], 'date': user_details['date'], 'sender_account': user_details['sender_account'], 'recipient_account': user_details['recipient_account'], 'recipient_name': user_details['recipient_name'], 'amount': user_details['amount'], 'description': user_details['description'], 'bank_name': user_details['bank_name'], 'iban': user_details['iban']}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        elif which == 'test':

            activation_path = 'email/test.html'
            receiver = ['osamudiamenjustine@gmail.com']

            email_subject = f"Test mail email"
            context_data = {'app_name':settings.APP_NAME, 'email': user_details['email'], 'user': user_details['user'],}
            email_body = get_template(activation_path).render(context_data)
            self.send_mail_directly(email_subject, email_body, receiver)
            # EmailThread(email_subject, email_body, receiver).start()

        else:

            messages.error(request, 'Unable to process request')

Email = Mailer()