import os
from PIL import Image
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import post_init, post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from common.dbtypes import CharField, TextField
from common.utils import random_string
from common.validators import validate_extension
from djblog.settings import MEDIA_ROOT, MEDIA_URL, AUTH_USER_MODEL

User = AUTH_USER_MODEL

CATEGORY_STATUS = [('A', 'Active'), ('I', 'Inactive'), ('X', 'Delete')]
POST_STATUS = [('P', 'Publish'), ('D', 'Draft'), ('S', 'Suspend'), ('X', 'Delete')]
COMMENT_STATUS = [('A', 'Active'), ('I', 'Inactive'), ('X', 'Delete')]


class Category(models.Model):
    title = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, null=True)
    status = CharField(max_length=1, choices=CATEGORY_STATUS, default='A')
    user = models.ForeignKey(User)
    updated_by = models.ForeignKey(User, db_column='updated_by', related_name='updated_by', null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title


def banner_name(instance, filename):
    return random_string(40)+'.jpg'

banner_storage = FileSystemStorage(location=MEDIA_ROOT+'/blog_banners', base_url=MEDIA_URL+'/blog_banners')


class Post(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    body = TextField()
    banner = models.ImageField(storage=banner_storage, upload_to=banner_name, max_length=255,
                               validators=[validate_extension])
    views = models.IntegerField(null=True)
    slug = models.SlugField(max_length=255, unique=True)
    status = CharField(max_length=1, choices=POST_STATUS, default='D')
    user = models.ForeignKey(User)
    updated_by = models.ForeignKey(User, db_column='updated_by', related_name='post_updated_by', null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    BANNER_SIZES = [(360, 230)]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)+'-'+random_string()
        super(Post, self).save(*args, **kwargs)

    def post_banner(self):
        return mark_safe(u'<img src="%s" style="width: 50%%; height: auto;" />' % self.banner.url)
    post_banner.short_description = 'Current Banner'

    def resize_banner(self):
        banner = Image.open(self.banner)
        for _ in self.BANNER_SIZES:
            name = '/{}x{}-'.format(_[0], _[1])+self.banner.name
            banner = banner.resize(_, Image.ANTIALIAS)
            banner.save(banner_storage.base_location + name, 'jpeg', quality=95)

    def delete_banner(self, current_banner):
        banner = current_banner.name
        current_banner.delete(save=False)
        for _ in self.BANNER_SIZES:
            sized_banner = banner_storage.base_location+'/{}x{}-'.format(_[0], _[1]) + banner
            if os.path.isfile(sized_banner):
                os.remove(sized_banner)


@receiver(post_init, sender=Post)
def backup_banner_path(sender, instance, **kwargs):
    instance._current_banner = instance.banner


@receiver(post_save, sender=Post)
def action_banner(sender, instance, **kwargs):
    if hasattr(instance, '_current_banner'):
        if instance._current_banner != instance.banner:
            instance.resize_banner()
            if instance._current_banner:
                instance.delete_banner(instance._current_banner)


class Comment(models.Model):
    comment = TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies')
    post = models.ForeignKey(Post)
    status = CharField(max_length=1, choices=COMMENT_STATUS, default='A')
    user = models.ForeignKey(User)
    updated_by = models.ForeignKey(User, db_column='updated_by', related_name='comment_updated_by', null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.comment
