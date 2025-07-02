from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
import uuid
import random

def generate_unique_account_number():
    while True:
        number = str(random.randint(1000000000, 9999999999))
        if not User.objects.filter(username=number).exists():
            return number

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None):

        # creates a user with the parameters
        if not email:
            raise ValueError('Email is required!')

        if password is None:
            raise ValueError('Password is required!')

        if not username:
            username = generate_unique_account_number()

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password=None):

        # create a superuser with the above parameters
        if not username:
            raise ValueError('Username is required!')

        if not email:
            raise ValueError('Email is required!')

        if password is None:
            raise ValueError('Password should not be empty')

        user = self.create_user(
            username=username.upper().strip(),
            email=self.normalize_email(email),
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):

    user_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    username = models.CharField(
        max_length=20, db_index=True, unique=True, blank=True)
    pic = models.ImageField(default='img/user.png',
                            null=True, blank=True, upload_to='uploads/profile/')
    email = models.CharField(max_length=100, db_index=True, unique=True,
                             verbose_name='email address', blank=True, null=True)

    date_joined = models.DateTimeField(
        verbose_name='date_joined', auto_now_add=True)
    last_login = models.DateTimeField(
        verbose_name='last_login', auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_support = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email',]

    objects = UserManager()

    @classmethod
    def users_signed_up_today(cls):
        today = timezone.now().date()
        return cls.objects.filter(date_joined__date=today).count()

    def __str__(self):
        return f'{self.username.upper()}'

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = 'Users'
        verbose_name_plural = 'Users'

class EmailSendCount(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    count = models.IntegerField(default=0)

    @property
    def increaseCount(self):
        self.count += 1

    @property
    def resetCount(self):
        self.count = 0

    @property
    def getCount(self):
        return self.count

    def __str__(self):
        return f'{self.user}, has used ({self.count})/({10})'

    class Meta:
        db_table = 'EmailCounter'
        verbose_name_plural = 'Email Send Count'

