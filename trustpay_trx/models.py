from django.db import models
from django.conf import settings
from decimal import Decimal
from django.db.models import Sum
import uuid

# My app imports
from trustpay_user.models import *

# Create your models here.
def generate_transaction_reference():
    # Generate a random UUID
    while True:
        unique_id = uuid.uuid4().hex[:16].upper()
        if not Transaction.objects.filter(trx_reference=str(unique_id)).exists():
            return str(unique_id)

def get_pending_status():
    object, _ = TransactionStatus.objects.get_or_create(transaction_status="Pending")
    return object.pk

class AllBank(models.Model):

    bank_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.bank_name

    class Meta:
        db_table = 'All Bank'
        verbose_name_plural = 'All Bank'

class TransactionType(models.Model):

    transaction_type = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.transaction_type

    class Meta:
        db_table = 'Transaction Type'
        verbose_name_plural = 'Transaction Type'

class TransactionStatus(models.Model):

    transaction_status = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.transaction_status

    class Meta:
        db_table = 'Transaction Status'
        verbose_name_plural = 'Transaction Status'

class LoanType(models.Model):

    loan_type = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.loan_type

    class Meta:
        db_table = 'LoanType'
        verbose_name_plural = 'LoanType'

class TransactionMethod(models.Model):

    method = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.method

    class Meta:
        db_table = 'Transaction Method'
        verbose_name_plural = 'Transaction Method'

class TransferType(models.Model):

    transfer_type = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.transfer_type

    class Meta:
        db_table = 'Transfer Type'
        verbose_name_plural = 'Transfer Type'

class TransactionCharges(models.Model):

    charges = models.CharField(max_length=10)
    trf_type = models.ForeignKey(to="TransferType", on_delete=models.CASCADE, blank=True, null=True, related_name='trf_type')

    def __str__(self):
        return f'{self.trf_type} - {self.charges}'

    class Meta:
        db_table = 'Transaction Charges'
        verbose_name_plural = 'Transaction Charges'

class CryptoWalletDetail(models.Model):

    crypto_type = models.CharField(max_length=30)
    crypto_network = models.CharField(max_length=100)
    crypto_address = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.crypto_type} - {self.crypto_network}'

    class Meta:
        db_table = 'Crypto Wallet Detail'
        verbose_name_plural = 'Crypto Wallet Detail'

class Balance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='balance')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    @property
    def decimal_amount(self):
        return Decimal(str(self.amount))

    def __str__(self):
        return f"{self.user.username} - Balance: {self.amount}"

    class Meta:
        db_table = 'Balance'
        verbose_name_plural = 'Balance'

class IMFCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_imf')
    code = models.CharField(max_length=20, blank=True, null=True, default="IMFDUS3WNO2")

    def __str__(self):
        return f"{self.user.username} - Code: {self.code}"

    class Meta:
        db_table = 'IMFCode'
        verbose_name_plural = 'IMFCode'

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.ForeignKey(to="TransactionType", on_delete=models.CASCADE, blank=True, null=True, related_name='trx_type')
    transaction_method = models.ForeignKey(to="TransactionMethod", on_delete=models.CASCADE, blank=True, null=True, related_name='trx_method')
    trx_status = models.ForeignKey(to="TransactionStatus", on_delete=models.SET_NULL, null=True, blank=True, default=get_pending_status, related_name='trx_status')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    trx_reference = models.CharField(max_length=100, null=True, blank=True, unique=True)
    description = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def failed_transactions(cls):
        failed_trxs = TransactionStatus.objects.filter(transaction_status='Failed').first()
        return cls.objects.filter(trx_status=failed_trxs).count() or 0

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        charge = kwargs.pop('charges', '0.00')
        reversal = kwargs.pop('reversal', False)

        if is_new and not self.trx_reference:
            self.trx_reference = generate_transaction_reference()

        super().save(*args, **kwargs)

        method = self.transaction_method.method.lower() if self.transaction_method else ''

        if is_new and method not in ['cheque deposit', 'crypto deposit']:

            balance, _ = Balance.objects.get_or_create(user=self.user)

            amount = Decimal(self.amount)
            charges = Decimal(charge)

            if not reversal:

                if self.transaction_type.transaction_type.lower() == 'credit':
                    balance.amount = balance.decimal_amount + amount
                else:
                    balance.amount = balance.decimal_amount - (amount + charges)
                balance.save()

    def get_origin(self):
        if hasattr(self, 'cheque_trx'):
            return 'Cheque Deposit'
        elif hasattr(self, 'crypto_trx'):
            return 'Crypto Deposit'
        elif hasattr(self, 'withdraw_trx'):
            return 'Withdrawal'
        elif hasattr(self, 'f_wire_trx'):
            return 'International Wire'
        elif hasattr(self, 'd_wire_trx'):
            return 'Domestic Wire'
        elif hasattr(self, 'transfer_trx'):
            return 'ACH Transfer'

        # Add more if you have other origins like Withdrawal
        return 'Unknown'

    def get_origin_status(self):
        related = getattr(self, 'cheque_trx', None) or getattr(self, 'crypto_trx', None) or getattr(self, 'withdraw_trx', None) or getattr(self, 'f_wire_trx', None) or getattr(self, 'd_wire_trx', None) or getattr(self, 'transfer_trx', None)
        if related and hasattr(related, 'trx_status'):
            return related.trx_status.transaction_status  # e.g. 'Pending', 'Completed'
        return 'N/A'

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"

    class Meta:
        db_table = 'Transaction'
        verbose_name_plural = 'Transactions'

class Withdrawal(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction = models.OneToOneField(to="Transaction", on_delete=models.SET_NULL, null=True, blank=True, related_name="withdraw_trx")
    transaction_method = models.ForeignKey(to="TransactionMethod", on_delete=models.CASCADE, blank=True, null=True, related_name='withdraw_method')
    trx_status = models.ForeignKey(to="TransactionStatus", on_delete=models.CASCADE, blank=True, null=True, default=get_pending_status, related_name='withdraw_trx_status')
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if not self.transaction and is_new:
            transaction_type = TransactionType.objects.filter(transaction_type='Debit').first()
            trx = Transaction.objects.create(
                user=self.user,
                transaction_type=transaction_type,
                transaction_method=self.transaction_method,
                amount=self.amount,
                description="Withdrawal",
            )
            self.transaction = trx
            super().save(update_fields=['transaction'])


    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"

    class Meta:
        db_table = 'Withdrawal'
        verbose_name_plural = 'Withdrawals'

class CryptoDeposit(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_crypto')
    crypto_type = models.ForeignKey(to="CryptoWalletDetail", on_delete=models.CASCADE, blank=True, null=True, related_name='trx_details')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_image = models.ImageField(upload_to='uploads/crypto/', null=True, blank=True)
    transaction = models.OneToOneField(to="Transaction", on_delete=models.SET_NULL, null=True, blank=True, related_name="crypto_trx")
    trx_status = models.ForeignKey(to="TransactionStatus", on_delete=models.SET_NULL, blank=True, null=True, default=get_pending_status, related_name='crypo_trx_status')
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def total_deposit_amount(cls):
        return cls.objects.aggregate(total=Sum('amount'))['total'] or 0

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if not self.transaction and is_new:
            transaction_type = TransactionType.objects.filter(transaction_type='Credit').first()
            transaction_method, _ = TransactionMethod.objects.get_or_create(method='Crypto Deposit')
            trx = Transaction.objects.create(
                user=self.user,
                transaction_type=transaction_type,
                transaction_method=transaction_method,
                amount=self.amount,
                description="Crypto Deposit",
            )
            self.transaction = trx
            super().save(update_fields=['transaction'])

    def __str__(self):
        return f"{self.user.username} - Crypto Deposit - {self.amount}"

class ChequeDeposit(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_cheque')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    cheque_front_img = models.ImageField(upload_to='uploads/cheque/', null=True, blank=True)
    cheque_back_img = models.ImageField(upload_to='uploads/cheque/', null=True, blank=True)
    transaction = models.OneToOneField(to="Transaction", on_delete=models.SET_NULL, null=True, blank=True, related_name="cheque_trx")
    trx_status = models.ForeignKey(to="TransactionStatus", on_delete=models.SET_NULL, blank=True, null=True, default=get_pending_status, related_name='cheque_trx_status')
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def total_deposit_amount(cls):
        trx_status = TransactionStatus.objects.filter(transaction_status='Completed').first()
        return cls.objects.filter(trx_status=trx_status).aggregate(total=Sum('amount'))['total'] or 0

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if not self.transaction and is_new:
            transaction_type = TransactionType.objects.filter(transaction_type='Credit').first()
            transaction_method, _ = TransactionMethod.objects.get_or_create(method='Cheque Deposit')
            trx = Transaction.objects.create(
                user=self.user,
                transaction_type=transaction_type,
                transaction_method=transaction_method,
                amount=self.amount,
                description="Cheque Deposit",
            )
            self.transaction = trx
            super().save(update_fields=['transaction'])

    def __str__(self):
        return f"{self.user.username} - Cheque Deposit - {self.amount}"

    class Meta:
        db_table = 'Cheque Deposit'
        verbose_name_plural = 'Cheque Deposit'

class ACHTransfer(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ach_user')
    account_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    routing_number = models.CharField(max_length=11, blank=True, null=True)
    transaction = models.OneToOneField(to="Transaction", on_delete=models.SET_NULL, null=True, blank=True, related_name="transfer_trx")
    trx_status = models.ForeignKey(to="TransactionStatus", on_delete=models.SET_NULL, blank=True, null=True, default=get_pending_status, related_name='ach_trx_status')
    account_type = models.ForeignKey(to=AccountType, on_delete=models.SET_NULL, null=True, blank=True, related_name="trx_acct")
    trx_reference = models.CharField(max_length=100, null=True, blank=True, unique=True, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if not self.transaction and is_new:

            transaction_type = TransactionType.objects.filter(transaction_type='Debit').first()
            transaction_method, _ = TransactionMethod.objects.get_or_create(method='Bank Transfer')
            description=f"Transfer to {self.account_name}: {self.note}"
            trf_type = TransferType.objects.get(transfer_type="ACH Transfer")
            charges = TransactionCharges.objects.get(trf_type=trf_type).charges

            # Debit sender
            trx = Transaction(
                user=self.user,
                transaction_type=transaction_type,
                transaction_method=transaction_method,
                amount=self.amount,
                description="ACH Transfer",
            )

            trx.save(charges=charges)

            self.transaction = trx
            super().save(update_fields=['transaction'])


    def __str__(self):
        return f"{self.user.username} to {self.account_name} - {self.amount}"

    class Meta:
        db_table = 'ACH Transfer'
        verbose_name_plural = 'ACH Transfers'

class DomesticWire(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='d_wire_user')
    account_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    routing_number = models.CharField(max_length=11, blank=True, null=True)
    transaction = models.OneToOneField(to="Transaction", on_delete=models.SET_NULL, null=True, blank=True, related_name="d_wire_trx")
    trx_status = models.ForeignKey(to="TransactionStatus", on_delete=models.SET_NULL, blank=True, null=True, default=get_pending_status, related_name='d_wire_trx_status')
    bank_name = models.ForeignKey(to=AllBank, on_delete=models.SET_NULL, null=True, blank=True, related_name="d_wire_banks")
    trx_reference = models.CharField(max_length=100, null=True, blank=True, unique=True, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if not self.transaction and is_new:

            transaction_type = TransactionType.objects.filter(transaction_type='Debit').first()
            transaction_method, _ = TransactionMethod.objects.get_or_create(method='Bank Transfer')
            description=f"Transfer to {self.account_name}: {self.note}"
            trf_type = TransferType.objects.get(transfer_type="Domestic Wire")
            charges = TransactionCharges.objects.get(trf_type=trf_type).charges

            # Debit sender
            trx = Transaction(
                user=self.user,
                transaction_type=transaction_type,
                transaction_method=transaction_method,
                amount=self.amount,
                description="Domestic Wire Transfer",
            )

            trx.save(charges=charges)

            self.transaction = trx
            super().save(update_fields=['transaction'])

    def __str__(self):
        return f"{self.user.username} to {self.account_name} - {self.amount}"

    class Meta:
        db_table = 'Domestic Wire'
        verbose_name_plural = 'Domestic Wire'

class InternationalWire(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='f_wire_user')
    account_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_address = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    swift_bic_code = models.CharField(max_length=11, blank=True, null=True)
    iban = models.CharField(max_length=34, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    transaction = models.OneToOneField(to="Transaction", on_delete=models.SET_NULL, null=True, blank=True, related_name="f_wire_trx")
    trx_status = models.ForeignKey(to="TransactionStatus", on_delete=models.SET_NULL, blank=True, null=True, default=get_pending_status, related_name='f_wire_trx_status')
    trx_reference = models.CharField(max_length=100, null=True, blank=True, unique=True, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if not self.transaction and is_new:

            transaction_type = TransactionType.objects.filter(transaction_type='Debit').first()
            transaction_method, _ = TransactionMethod.objects.get_or_create(method='Bank Transfer')
            description=f"Transfer to {self.account_name}: {self.note}"
            trf_type = TransferType.objects.get(transfer_type="International Wire")
            charges = TransactionCharges.objects.get(trf_type=trf_type).charges

            # Debit sender
            trx = Transaction(
                user=self.user,
                transaction_type=transaction_type,
                transaction_method=transaction_method,
                amount=self.amount,
                description="International Wire Transfer",
            )

            trx.save(charges=charges)

            self.transaction = trx
            super().save(update_fields=['transaction'])

    def __str__(self):
        return f"{self.user.username} to {self.account_name} - {self.amount}"

    class Meta:
        db_table = 'International Wire'
        verbose_name_plural = 'International Wire'

class MortgageApplication(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mortgage_user')
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    employment_status = models.ForeignKey(to=EmploymentStatus, on_delete=models.CASCADE, related_name='mortgage_emp_status')
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.ForeignKey(to=TransactionStatus, on_delete=models.CASCADE, related_name='mortgage_status', default=get_pending_status)
    credit_score = models.IntegerField()
    credit_report = models.FileField(upload_to="credit_reports/")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - mortgage application"

    class Meta:
        db_table = 'Mortgage Application'
        verbose_name_plural = 'Mortgage Application'

class EmploymentAndPropertyAppraisal(models.Model):
    application = models.OneToOneField(MortgageApplication, on_delete=models.CASCADE, related_name='mortgage_application')
    employer_name = models.CharField(max_length=100)
    hr_contact = models.CharField(max_length=100)
    proof_of_income = models.FileField(upload_to="income_proofs/")
    property_value = models.DecimalField(max_digits=12, decimal_places=2)
    appraisal_report = models.FileField(upload_to="appraisals/")
    sales_contract = models.FileField(upload_to="property_contracts/", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.user.username} - employment and property appraisal"

    class Meta:
        db_table = 'Employment And Property Appraisal'
        verbose_name_plural = 'Employment And Property Appraisal'

class MortgageDeposit(models.Model):
    application = models.OneToOneField(MortgageApplication, on_delete=models.CASCADE, related_name='mortgage_deposit')
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved = models.BooleanField(default=False)
    cheque_front_img = models.ImageField(upload_to='uploads/cheque/', null=True, blank=True)
    cheque_back_img = models.ImageField(upload_to='uploads/cheque/', null=True, blank=True)
    trx_reference = models.CharField(max_length=100, null=True, blank=True, unique=True, default=generate_transaction_reference)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application} - morgage deposit"

    class Meta:
        db_table = 'Mortgage Deposit'
        verbose_name_plural = 'Mortgage Deposit'

class LoanRepayment(models.Model):
    application = models.ForeignKey(MortgageApplication, on_delete=models.CASCADE, related_name='mortgage_repayment')
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application} - morgage repayment"

    class Meta:
        db_table = 'Loan Repayment'
        verbose_name_plural = 'Loan Repayment'


