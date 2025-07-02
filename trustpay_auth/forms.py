# My Django app imports
from django import forms

# My App imports
from trustpay_auth.models import *
from trustpay_user.models import *

class RegisterAccount(forms.ModelForm):

    email = forms.EmailField(help_text='Enter a valid email address', empty_value=None, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'type': 'email'
        }
    ))

    account_type = forms.ModelChoiceField(queryset=AccountType.objects.all(), empty_label="(Select account type)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    password = forms.CharField(help_text='Enter Password', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
            'id':'password',
            'name':'password'
        }
    ))

    confirm_password = forms.CharField(help_text='Confirm Password', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
            'id':'ConfirmPassword',
            'name':'confirm_password',
        }
    ))

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if password is None:
            raise forms.ValidationError("Password is required!")

        if len(password) < 6 :
            raise forms.ValidationError("Password is too short!")

        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get('confirm_password')
        password = self.cleaned_data.get('password')

        if confirm_password is None:
            raise forms.ValidationError("Confirm Password is required!")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords and Confirm Password do not match!")

        return confirm_password

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email.lower().strip()).exists():
            raise forms.ValidationError('Email Already taken!')

        return email

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password', 'account_type')