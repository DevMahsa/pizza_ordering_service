from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .constants import ORDER_SIZE, ORDER_STATUS, ORDER_TITLE


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Detail(models.Model):
    flavour = models.PositiveSmallIntegerField(
        choices=ORDER_TITLE,
        default=1
    )
    size = models.PositiveSmallIntegerField(
        choices=ORDER_SIZE,
        default=1
    )
    quantity = models.PositiveIntegerField(default=1)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )


class Order(models.Model):
    """Order object"""
    name = models.CharField(default='pizza',
                            max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    status = models.PositiveSmallIntegerField(
        choices=ORDER_STATUS,
        default=1
    )
    detail = models.ManyToManyField('Detail', blank=False)
    phone = models.CharField(_('Phone'),
                             max_length=16,
                             help_text=_('Phone for driver to contact'))
    address = models.TextField(_('Address'),
                               help_text=_('Address for pizza delivery'))

    def __str__(self):
        return u'[{name} - {status}] - {user} '.format(
            name=self.name,
            status=self.get_status_display(),
            user=self.user.name
        )
