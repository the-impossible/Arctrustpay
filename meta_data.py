import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arc_trustpay.settings')
django.setup()

from trustpay_user.models import *
from trustpay_auth.models import *
from trustpay_trx.models import *

# Create Gender
users_genders = ['Male', 'Female', 'Other']
[Gender.objects.get_or_create(gender_title=gender) for gender in users_genders]

# Create Relationship Status
relationship_status = ['Single', 'Married', 'Divorced', 'Widowed', 'Other']
[RelationshipStatus.objects.get_or_create(status_title=status) for status in relationship_status]

# Create Employment Status
employment_status = ['Employed', 'Self-Employed', 'Unemployed', 'Student', 'Retired', 'Other']
[EmploymentStatus.objects.get_or_create(status_title=status) for status in employment_status]

# Create Account Type
acct_types = ['Checking', 'Savings']
[AccountType.objects.get_or_create(account_type=acct_type) for acct_type in acct_types]

# Create Transaction Type
trx_types = ['Credit', 'Debit']
[TransactionType.objects.get_or_create(transaction_type=trx_type) for trx_type in trx_types]

#Transfer Type
trx_types = ['Internal Transfer', 'ACH Transfer', 'Domestic Wire', 'International Wire']
[TransferType.objects.get_or_create(transfer_type=trf_type) for trf_type in trx_types]

# Create Transaction Type
transfer_charges = [
    {
        'charges': '0',
        'trf_type': TransferType.objects.get_or_create(transfer_type='Internal Transfer')[0],
    },
    {
        'charges': '3',
        'trf_type': TransferType.objects.get_or_create(transfer_type='ACH Transfer')[0],
    },
    {
        'charges': '25',
        'trf_type': TransferType.objects.get_or_create(transfer_type='Domestic Wire')[0],
    },
    {
        'charges': '45',
        'trf_type': TransferType.objects.get_or_create(transfer_type='International Wire')[0],
    },
]
[TransactionCharges.objects.get_or_create(**trf_type) for trf_type in transfer_charges]

# Create Transaction status
trx_status = ['Pending', 'Completed', 'Failed']
[TransactionStatus.objects.get_or_create(transaction_status=status) for status in trx_status]

# Loan Types
# loan_type = ['Personal', 'Mortgage',]
# [LoanType.objects.get_or_create(loan_type=loan) for loan in loan_type]

# Create Transaction Method
trx_method = ['Bank Transfer', 'Cheque Deposit', 'Crypto Deposit', 'Internal Transfer', 'Other']
[TransactionMethod.objects.get_or_create(method=method) for method in trx_method]

# Crypto wallet details
wallet_details = [
    {
        'crypto_type': 'ETH',
        'crypto_network': 'Ethereum (ERC20)',
        'crypto_address': '0x165d9f137d54DB90936c64B6157f0CDD54158265',
    },
    {
        'crypto_type': 'USDT',
        'crypto_network': 'USDT (TRC20)',
        'crypto_address': 'TMA95ECXf8tgcSCyHvmtfuGnCmhhxh7Z9W',
    },
    {
        'crypto_type': 'BTC',
        'crypto_network': 'BTC',
        'crypto_address': 'bc1qj4lwvsm8e3r6x7cav7rqspsugnqyfuf7tq6mhy',
    },
]

[CryptoWalletDetail.objects.get_or_create(**detail) for detail in wallet_details]

# Account Manager
manager_details = [
    {
        'first_name': 'Michael',
        'last_name': 'Wood',
        'phone': '+1 (870) 217-2243',
        'email': 'info@arctrustpay.com',
    },
]

[AccountManagerInfo.objects.get_or_create(**detail) for detail in manager_details]

# Create Bank
banks = [
    "Bank of America",
    "JPMorgan Chase",
    "Wells Fargo",
    "Citibank",
    "U.S. Bank",
    "PNC Bank",
    "Truist Bank",
    "TD Bank",
    "Capital One",
    "Fifth Third Bank",
    "Regions Bank",
    "KeyBank",
    "Ally Bank",
    "Huntington National Bank",
    "BMO Harris Bank",
    "Citizens Bank",
    "First Republic Bank",
    "M&T Bank",
    "Comerica Bank",
    "Zions Bank",
    "Synovus Bank",
    "Bank of the West",
    "Frost Bank",
    "Silicon Valley Bank",
    "Union Bank",
    "Banner Bank",
    "Bank OZK",
    "Valley National Bank",
    "East West Bank",
    "UMB Bank",
    "City National Bank",
    "BankUnited",
    "Associated Bank",
    "Texas Capital Bank",
    "First Horizon Bank",
    "Prosperity Bank",
    "Cathay Bank",
    "Pinnacle Bank",
    "Amegy Bank",
    "Old National Bank",
    "Western Alliance Bank",
    "First Citizens Bank",
    "Pacific Western Bank",
    "Customers Bank",
    "SouthState Bank",
    "Glacier Bank",
    "Independent Bank",
    "Cadence Bank",
    "Columbia Bank",
    "Commerce Bank",
    "TowneBank",
    "FirstBank",
    "Bank of Hope",
    "Other"
]
[AllBank.objects.get_or_create(bank_name=bank) for bank in banks]
