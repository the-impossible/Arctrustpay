# My django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.hashers import make_password, check_password

# My app imports
from trustpay_user.models import *
from trustpay_user.forms import *
from trustpay_trx.models import *

# Create your views here.
class DashboardPageView(LoginRequiredMixin, TemplateView, SuccessMessageMixin):
    template_name = "backend/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['total_crypto'] = CryptoDeposit.total_deposit_amount()
            context['total_cheque'] = ChequeDeposit.total_deposit_amount()
            context['failed_trxs'] = Transaction.failed_transactions()
            context['signed_up_today'] = User.users_signed_up_today()
            context['object_list'] = Transaction.objects.all().order_by('-timestamp')[:20]
        else:

            context['object_list'] = Transaction.objects.filter(user=self.request.user).order_by('-timestamp')[:20]
        return context

class AccountManagerView(LoginRequiredMixin, TemplateView, SuccessMessageMixin):
    template_name = "backend/account_manager.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = AccountManagerInfo.objects.all().first()
        return context

class UserAccountPageView(LoginRequiredMixin, View, SuccessMessageMixin):

    form = PersonalInfoForm
    form2 = ContactInfoForm
    form3 = BankAccountInfoForm
    template_name = "backend/users/account_details.html"
    update_details = ''
    change_password = ''
    change_pin = ''

    def get(self, request):
        user = request.user

        # Retrieve existing records tied to the user
        personal_info_instance = PersonalInfo.objects.filter(user=user).first()
        contact_info_instance = ContactInfo.objects.filter(user=user).first()
        bank_account_info = BankAccountInfo.objects.filter(user=user).first()

        form = self.form(instance=personal_info_instance)
        form2 = self.form2(instance=contact_info_instance)
        form3 = self.form3(instance=bank_account_info)

        if user.is_verified:
            # Disable all fields if already filled
            for name, field in form.fields.items():
                if getattr(personal_info_instance, name):
                    field.widget.attrs['disabled'] = True

            for name, field in form2.fields.items():
                if getattr(contact_info_instance, name):
                    field.widget.attrs['disabled'] = True

            for name, field in form3.fields.items():
                if name != 'profile_picture' and getattr(bank_account_info, name):
                    field.widget.attrs['disabled'] = True

        context = {
            'account_form': form,
            'contact_form': form2,
            'bank_account_form': form3,
            'personal_info': personal_info_instance,
            'contact_info': contact_info_instance,
            'bank_account_info': bank_account_info,
            'update_details': 'active',
            'change_password': self.change_password,
            'change_pin': self.change_pin,
            'user': user,
        }

        return render(request, self.template_name, context)

    def post(self, request):

        user = request.user

        # Retrieve existing records tied to the user
        personal_info_instance = PersonalInfo.objects.filter(user=user).first()
        contact_info_instance = ContactInfo.objects.filter(user=user).first()
        bank_account_info = BankAccountInfo.objects.filter(user=user).first()

        # Bind the forms with POST data and the existing instances
        form = self.form(request.POST, instance=personal_info_instance)
        form2 = self.form2(request.POST, instance=contact_info_instance)
        form3 = self.form3(request.POST, request.FILES, instance=bank_account_info)

        if 'account_details' in request.POST:

            if form.is_valid() and form2.is_valid() and form3.is_valid():

                state = request.POST['state']
                country = request.POST['country']

                profile_picture = form3.cleaned_data.get('profile_picture')
                if profile_picture:
                    request.user.pic = profile_picture

                form.save()
                form3.save()

                request.user.is_verified = True
                request.user.save()

                contact_info = form2.save(commit=False)
                contact_info.state = state
                contact_info.country = country
                contact_info.save()

                messages.success(request, 'Account details updated successfully!')
                return redirect('user:account_details')

            else:
                self.update_details = 'active'

                messages.error(request, 'Please correct the errors below.')
                context = {
                    'account_form': form,
                    'contact_form': form2,
                    'bank_account_form': form3,
                    'update_details': self.update_details,
                }

                return render(request, self.template_name, context)

        elif 'change_password' in request.POST:

            # self.object = User.objects.filter(user_id=request.user.user_id).first()

            self.change_password = 'active'
            oldPassword = request.POST.get('oldPassword')
            newPassword = request.POST.get('newPassword')
            confirmPassword = request.POST.get('confirmPassword')

            context = {
                'account_form': form,
                'contact_form': form2,
                'bank_account_form': form3,
                'oldPassword': oldPassword,
                'newPassword': newPassword,
                'confirmPassword': confirmPassword,
                'change_password': self.change_password,
                'user': user,
            }

            route = render(request, template_name=self.template_name, context=context)

            if (newPassword != confirmPassword):
                messages.error(
                    request, 'New password and confirm password does not match!')
                return route

            if (len(confirmPassword) < 6):
                messages.error(
                    request, 'password too short! should not be less than 6 characters')
                return route

            if not user.check_password(oldPassword):
                messages.error(request, 'Old password incorrect!')
                return route

            user.set_password(newPassword)
            user.save()

            messages.success(
                request, 'Password reset successful, you can now login!!')

            return redirect('auth:login')

        elif 'create_pin' in request.POST:

            self.change_pin = 'active'
            newPin = request.POST.get('newPin')
            confirmPin = request.POST.get('confirmPin')

            context = {
                'account_form': form,
                'contact_form': form2,
                'bank_account_form': form3,
                'newPin': newPin,
                'confirmPin': confirmPin,
                'change_pin':self.change_pin,
                'user': user,
            }

            route = render(request, template_name=self.template_name, context=context)

            if (newPin != confirmPin):
                messages.error(
                    request, 'New pin and confirm pin does not match!')
                return route

            if (len(confirmPin) != 4):
                messages.error(
                    request, 'pin should be exactly four digits')
                return route

            tPin = TransactionPin.objects.get_or_create(user=request.user, pin=make_password(confirmPin))

            messages.success(request, 'Pin created successfully!')

            return redirect('user:account_details')

        elif 'update_pin' in request.POST:

            self.change_pin = 'active'
            oldPin = request.POST.get('oldPin')
            newPin = request.POST.get('newPin')
            confirmPin = request.POST.get('confirmPin')

            context = {
                'account_form': form,
                'contact_form': form2,
                'bank_account_form': form3,
                'oldPin': oldPin,
                'newPin': newPin,
                'confirmPin': confirmPin,
                'change_pin':self.change_pin,
                'user': user,
            }

            route = render(request, template_name=self.template_name, context=context)

            if (newPin != confirmPin):
                messages.error(
                    request, 'New pin and confirm pin does not match!')
                return route

            if (len(confirmPin) != 4):
                messages.error(
                    request, 'Transaction pin should be exactly four digits')
                return route

            storePin = TransactionPin.objects.get(user=request.user)
            if check_password(oldPin, storePin.pin):
                messages.success(request, 'Transaction pin updated successfully!')
                storePin.pin = make_password(confirmPin)
                storePin.save()
                return redirect('user:account_details')
            else:
                messages.error(request, 'Old password incorrect!')
                return route

        else:
            messages.error(request, 'Unable to process request!')
            return route


