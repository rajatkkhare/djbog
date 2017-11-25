import os
from random import randint
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import pre_save, post_init, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)

from common.utils import random_string
from common.validators import validate_extension
from djblog.settings import MEDIA_ROOT, MEDIA_URL


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **kwargs)
        if 'username' not in kwargs or not kwargs['username']:
            user.username = generate_username(kwargs['first_name'])
        else:
            user.username = kwargs['username']
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.create_user(email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        return user


def avatar_name(instance, filename):
    return random_string(40)+'.jpg'
avatar_storage = FileSystemStorage(location=MEDIA_ROOT+'/avatars', base_url=MEDIA_URL+'/avatars')


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, unique=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    avatar = models.ImageField(storage=avatar_storage, upload_to=avatar_name, max_length=255,
                               validators=[validate_extension], blank=True, null=True)
    bio = models.CharField(max_length=140, blank=True, default="")
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return "@{}".format(self.username)

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def send_registration_mail(self):
        msg_html = render_to_string('accounts/emails/registration-email.html', {'user': self})
        msg = EmailMultiAlternatives('Welcome to DJ Blog', msg_html, to=[self.email])
        msg.content_subtype = "html"
        return msg.send()

    def avatar_or_default(self, default_path="/storage/avatars/default-avatar.png"):
        if self.avatar:
            return self.avatar.url
        return default_path

    def user_avatar(self):
        return mark_safe(u'<img src="%s" style="width: 50%%; height: auto;" />' % self.avatar.url)
    user_avatar.short_description = 'User Avatar'

    def delete_avatar(self, current_avatar):
        avatar = current_avatar.name
        avatar = avatar_storage.base_location+'/'+avatar
        if os.path.isfile(avatar):
            os.remove(avatar)


def generate_username(username):
    username = slugify(username)
    if User.objects.filter(username=username).count():
        return generate_username(username+str(randint(1, 1000)))
    return username


@receiver(post_init, sender=User)
def backup_avatar_path(sender, instance, **kwargs):
    instance._current_avatar = instance.avatar


@receiver(pre_save, sender=User)
def set_username(sender, instance, **kwargs):
    if not instance.username:
        instance.username = generate_username(instance.first_name)


@receiver(post_save, sender=User)
def action_avatar(sender, instance, **kwargs):
    if hasattr(instance, '_current_avatar'):
        if instance._current_avatar != instance.avatar:
            if instance._current_avatar:
                instance.delete_avatar(instance._current_avatar)
