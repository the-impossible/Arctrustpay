from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from datetime import date

# Create your models here.
class Gender(models.Model):
    gender_title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.gender_title

    class Meta:
        db_table = 'Gender'
        verbose_name_plural = 'Gender'

class AccountType(models.Model):
    account_type = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.account_type

    class Meta:
        db_table = 'Account Type'
        verbose_name_plural = 'Account Type'

class RelationshipStatus(models.Model):
    status_title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.status_title

    class Meta:
        db_table = 'Relationship'
        verbose_name_plural = 'Relationship'

class EmploymentStatus(models.Model):
    status_title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.status_title

    class Meta:
        db_table = 'Employment Status'
        verbose_name_plural = 'Employment Status'

class PersonalInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='personal_info')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.ForeignKey(to="Gender", on_delete=models.CASCADE, blank=True, null=True, related_name='gender')
    relationship_status = models.ForeignKey(to="RelationshipStatus", on_delete=models.CASCADE, blank=True, null=True, related_name='rel_status')

    @property
    def age(self):
        today = date.today()
        if self.date_of_birth:
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'Personal Info'
        verbose_name_plural = 'Personal Info'

class ContactInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contact_info')
    phone_number = PhoneNumberField(db_index=True, unique=True, blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Contact Info"

    class Meta:
        db_table = 'Contact Info'
        verbose_name_plural = 'Contact Info'

class BankAccountInfo(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_info')
    account_type = models.ForeignKey(to="AccountType", on_delete=models.CASCADE, blank=True, null=True, related_name='acct_type')
    employment_status = models.ForeignKey(to="EmploymentStatus", on_delete=models.CASCADE, blank=True, null=True, related_name='emp_status')
    issued_id = models.ImageField(upload_to='uploads/issued_id/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_type}"

    class Meta:
        db_table = 'Bank Account Info'
        verbose_name_plural = 'Bank Account Info'

class TransactionPin(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trx_pin')
    pin = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user}"

    class Meta:
        db_table = 'Transaction Pin'
        verbose_name_plural = 'Transaction Pin'

class AccountManagerInfo(models.Model):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, db_index=True, unique=True, verbose_name='email address', blank=True, null=True)
    pic = models.ImageField(default='img/user.png', null=True, blank=True, upload_to='uploads/profile/')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'Account Manager Info'
        verbose_name_plural = 'Account Manager Info'
