# My Django app imports
from django import forms
from phonenumber_field.formfields import SplitPhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

# My App imports
from trustpay_auth.models import *
from trustpay_user.models import *

class PersonalInfoForm(forms.ModelForm):

    first_name = forms.CharField(help_text='Enter your first name', strip=True, empty_value=None, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'text'
        }
    ))

    last_name = forms.CharField(help_text='Enter your first name', strip=True, empty_value=None, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'text'
        }
    ))

    date_of_birth = forms.DateField(help_text='Enter your date of birth', widget=forms.DateInput(
        attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'YYYY-MM-DD'
        }))

    gender = forms.ModelChoiceField(queryset=Gender.objects.all(), empty_label="(Select gender)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    relationship_status = forms.ModelChoiceField(queryset=RelationshipStatus.objects.all(), empty_label="(Select relationship_status)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    class Meta:
        model = PersonalInfo
        fields = ('first_name', 'last_name', 'date_of_birth', 'gender', 'relationship_status')

class ContactInfoForm(forms.ModelForm):

    phone_number = SplitPhoneNumberField()

    city = forms.CharField(help_text='Enter your city', strip=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))

    zip_code = forms.CharField(help_text='Enter your zip code', strip=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))

    address = forms.CharField(help_text='Enter address', strip=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))

    class Meta:
        model = ContactInfo
        fields = ('phone_number', 'address', 'city', 'zip_code')

class BankAccountInfoForm(forms.ModelForm):

    profile_picture = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    issued_id = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    employment_status = forms.ModelChoiceField(queryset=EmploymentStatus.objects.all(), empty_label="(Select employment_status)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    class Meta:
        model = BankAccountInfo
        fields = ('employment_status', 'issued_id')

