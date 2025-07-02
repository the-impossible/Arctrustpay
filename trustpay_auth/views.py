# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

# My app imports
from trustpay_auth.models import *
from trustpay_auth.forms import *
from trustpay_email.mailer import *

#Email
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from trustpay_email.mailer import *

# Create your views here.
class LoginPageView(View):
    template_name = "backend/auth/signin.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        if username and password:
            # Authenticate user
            user = authenticate(
                request, username=username.upper(), password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'You are now signed in {user.email}')
                    nxt = request.GET.get('next', None)

                    if nxt is None:
                        return redirect('user:dashboard')
                    return redirect(self.request.GET.get('next', None))
                else:
                    messages.warning(
                        request, 'Account not active contact the administrator')
                    return redirect('auth:login')
            messages.warning(request, 'Invalid login credentials')
            return redirect('auth:login')
        else:
            messages.error(request, 'All fields are required!!')
            return redirect('auth:login')

class RegisterPageView(View):
    template_name = "backend/auth/signup.html"
    form = RegisterAccount

    def get(self, request):
        context = {
            'form': self.form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form(request.POST)

        if form.is_valid():

            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            account_type = form.cleaned_data.get('account_type')

            # Create user using manager to ensure username is auto-generated
            user = User.objects.create_user(email=email, password=password)

            # Then create related records
            PersonalInfo.objects.create(user=user)
            ContactInfo.objects.create(user=user)
            BankAccountInfo.objects.create(user=user, account_type=account_type)

            # Send email
            user_details = {
                'account_number': user.username,
                'email': email,
            }

            Email.send(user_details, 'welcome')
            messages.success(request, "Account created successfully, You will receive an email with your account details shortly.")

            return redirect('auth:login')

        else:

            context = {
                'form':form
            }

            messages.error(request, form.errors.as_text())
            return render(request, self.template_name, context)

class EmailPreviewPageView(View):
    template_name = "email/support_request.html"

    def get(self, request):
        user_details = {
            'email':'nccsteam@gmail.com',
            'user':'nccsteam@gmail.com',
        }
        Email.send(user_details, 'test')

class SignOutPageView(TemplateView):
    template_name = "backend/auth/signout.html"

class LogoutView(LoginRequiredMixin, View):
    login_url = 'auth:login'
    def post(self, request):
        logout(request)
        messages.success(request, 'You are successfully logged out, to continue login again')
        return redirect('auth:signout')

class ForgotPasswordPageView(View):

    template_name = "backend/auth/forgot-password.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email').lower()
        if email:
            user = User.objects.filter(email=email)
            if user.exists():
                current_site = get_current_site(request).domain
                data = user[0]
                user_details = {
                    'fullname':data.personal_info,
                    'email': data.email,
                    'domain':current_site,
                    'uid': urlsafe_base64_encode(force_bytes(data.user_id)),
                    'token': email_activation_token.make_token(data),
                }
                Email.send(user_details, 'reset')
                messages.success(request, 'A mail has been sent to your mailbox to enable you reset your password!')
            else:
                messages.error(request, "Email address doesn't exist!")
        return render(request, self.template_name)

class ResetPasswordPageView(View):
    template_name = "backend/auth/reset-password.html"

    def get(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        user_id = force_str(force_bytes(urlsafe_base64_decode(uidb64)))
        try:
            user = User.objects.get(user_id=user_id)
            if email_activation_token.check_token(user, token):
                messages.info(request, 'Create a password for your account!')
                return render(request, self.template_name, context)
            else:
                messages.info(request, 'Link broken or Invalid reset link, Please Request a new one!')
                return redirect('auth:forget-password')

        except User.DoesNotExist:
            messages.error(request, 'Oops User not found, hence password cannot be changed, kindly request for a new link!')
            return redirect('auth:forget-password')

    def post(self, request, uidb64, token):

        user_id = force_str(force_bytes(urlsafe_base64_decode(uidb64)).decode())
        context = {
            'uidb64':uidb64,
            'token':token
        }

        try:
            user = User.objects.get(user_id=user_id)
            password1 = request.POST['password']
            password2 = request.POST['confirmPassword']

            if(password1 != password2):
                messages.error(request, 'Password don\'t match!')
                return render(request, self.template_name, context)

            if(len(password1) < 6):
                messages.error(request, 'Password too short!')
                return render(request, self.template_name, context)

            user.set_password(password1)
            user.save()
            messages.success(request, 'Password Changed you can now login with new password')

            return redirect('auth:login')

        except User.DoesNotExist:
            messages.error(request, 'Oops user does not exist!')
            return redirect('auth:forget-password')

