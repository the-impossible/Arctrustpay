# My Django app imports
from django import forms
from phonenumber_field.formfields import SplitPhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

# My App imports
from trustpay_auth.models import *
from trustpay_user.models import *
from trustpay_trx.models import *

class DepositEnquiryForm(forms.Form):

    deposit_amount = forms.IntegerField(help_text='Enter the deposit_amount', min_value=1, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': 1,
            'placeholder': 'Deposit Amount',
        }
    ))

    payment_method = forms.ModelChoiceField(queryset=CryptoWalletDetail.objects.all(), empty_label="(Select payment_method)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

class CompleteDepositEnquiryForm(forms.Form):

    payment_proof = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg',
            'id': 'paymentProof',
        }
    ))

class ChequeDepositForm(forms.Form):

    deposit_amount = forms.IntegerField(help_text='Enter the deposit_amount', min_value=1, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': 1,
            'placeholder': 'Deposit Amount',
        }
    ))

    front_of_cheque = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg',
            'id': 'frontCheque',
        }
    ))

    back_of_cheque = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg',
            'id': 'backCheque',
        }
    ))

class InternalTransferForm(forms.Form):

    amount = forms.IntegerField(help_text='Enter amount', min_value=1, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': 1,
            'placeholder': 'Transfer Amount',
        }
    ))

    description = forms.CharField(required=False, help_text="Enter Description", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "(e.g., 'Rent savings')",
        }
    ))

class ACHTransferForm(forms.Form):

    account_name = forms.CharField(help_text="Enter account name", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))

    amount = forms.IntegerField(help_text='Enter amount', min_value=1, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': 1,
            'placeholder': 'Transfer Amount',
            'inputmode':"numeric",
        }
    ))

    routing_number = forms.CharField(help_text="Enter routing number", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter routing number",
            'inputmode':"numeric",
            'pattern':"\d{9}",
            'maxlength':"9",
        }
    ))

    account_number = forms.CharField(help_text="Enter account number", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter account number",
            'type': "number",
            'inputmode':"numeric",
        }
    ))

    account_type = forms.ModelChoiceField(queryset=AccountType.objects.all(), empty_label="(Select account_type)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    note = forms.CharField(required=False, help_text="Enter Description", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "(e.g., 'Rent savings')",
        }
    ))

class DomesticWireForm(forms.Form):

    account_name = forms.CharField(help_text="Enter account name", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))

    account_number = forms.CharField(help_text="Enter account number", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter account number",
            'inputmode':"numeric",
        }
    ))

    bank_name = forms.ModelChoiceField(queryset=AllBank.objects.all(), empty_label="(Select bank)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    amount = forms.IntegerField(help_text='Enter amount', min_value=1, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': 1,
            'placeholder': 'Transfer Amount',
            'inputmode':"numeric",
        }
    ))

    routing_number = forms.CharField(help_text="Enter routing number", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter routing number",
            'inputmode':"numeric",
            'pattern':"\d{9}",
            'maxlength':"9",
        }
    ))

    note = forms.CharField(required=False, help_text="Enter Description", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "(e.g., 'Rent savings')",
        }
    ))

class InternationalWireForm(forms.Form):

    account_name = forms.CharField(help_text="Enter account name", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))

    account_number = forms.CharField(help_text="Enter account number", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter account number",
            'inputmode':"numeric",
        }
    ))

    amount = forms.IntegerField(help_text='Enter amount', min_value=1, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': 1,
            'placeholder': 'Transfer Amount',
            'inputmode':"numeric",
        }
    ))

    bank_name = forms.CharField(help_text="Enter bank_name", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter bank_name",
        }
    ))

    swift_bic_code = forms.CharField(help_text="Enter swift bic code", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter swift bic code",
        }
    ))

    iban = forms.CharField(help_text="Enter IBAN", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter IBAN",
        }
    ))

    bank_address = forms.CharField(help_text="Enter bank address", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter bank address",
        }
    ))

    note = forms.CharField(required=False, help_text="Enter Description", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "(e.g., 'Rent savings')",
        }
    ))

class MortgageApplicationForm(forms.ModelForm):

    amount_requested = forms.IntegerField(help_text='amount requested', min_value=1, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': 1,
            'placeholder': 'Amount Requested',
            'inputmode':"numeric",
        }
    ))

    employment_status = forms.ModelChoiceField(queryset=EmploymentStatus.objects.all(), empty_label="(Select employment status)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    annual_income = forms.IntegerField(help_text='annual income', min_value=1, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': 1,
            'placeholder': 'annual income',
            'inputmode':"numeric",
        }
    ))

    credit_score = forms.IntegerField(help_text='credit score', min_value=1, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': 1,
            'placeholder': 'credit score',
            'inputmode':"numeric",
        }
    ))

    credit_report = forms.FileField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': '.pdf, .doc, .docx, image/png, image/jpeg'
        }
    ))

    class Meta:
        model = MortgageApplication
        fields = ('amount_requested', 'employment_status', 'annual_income', 'credit_score', 'credit_report')

class EmploymentAndPropertyAppraisalForm(forms.ModelForm):

    employer_name = forms.CharField(help_text="Enter employer name", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "(e.g., 'John Doe')",
        }
    ))

    hr_contact = forms.CharField(help_text="Enter HR contact", widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "HR phone number",
        }
    ))

    proof_of_income = forms.FileField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': '.pdf, .doc, .docx, image/png, image/jpeg'
        }
    ))

    property_value = forms.IntegerField(help_text='property value', min_value=1, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': 1,
            'placeholder': 'property value',
            'inputmode':"numeric",
        }
    ))

    appraisal_report = forms.FileField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': '.pdf, .doc, .docx, image/png, image/jpeg'
        }
    ))

    sales_contract = forms.FileField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': '.pdf, .doc, .docx, image/png, image/jpeg'
        }
    ))

    class Meta:
        model = EmploymentAndPropertyAppraisal
        fields = ('employer_name', 'hr_contact', 'proof_of_income', 'property_value', 'appraisal_report', 'sales_contract')

class MortgateDepositForm(forms.Form):

    front_of_cheque = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg',
            'id': 'frontCheque',
        }
    ))

    back_of_cheque = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg',
            'id': 'backCheque',
        }
    ))