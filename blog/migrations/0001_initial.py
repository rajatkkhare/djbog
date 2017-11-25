# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-09 20:38
from __future__ import unicode_literals

import blog.models
import common.dbtypes
import common.validators
from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(max_length=255, null=True)),
                ('status', common.dbtypes.CharField(choices=[('A', 'Active'), ('I', 'Inactive'), ('X', 'Delete')], default='A', max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'verbose_name': 'Category',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', common.dbtypes.TextField()),
                ('status', common.dbtypes.CharField(choices=[('A', 'Active'), ('I', 'Inactive'), ('X', 'Delete')], default='A', max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='blog.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('short_description', models.CharField(max_length=255)),
                ('body', common.dbtypes.TextField()),
                ('banner', models.ImageField(max_length=255, storage=django.core.files.storage.FileSystemStorage(base_url='/storage//blog_banners', location='/home/rajat/pythonPro/djblog/storage/blog_banners'), upload_to=blog.models.banner_name, validators=[common.validators.validate_extension])),
                ('views', models.IntegerField(null=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('status', common.dbtypes.CharField(choices=[('P', 'Publish'), ('D', 'Draft'), ('S', 'Suspend'), ('X', 'Delete')], default='D', max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Category')),
                ('updated_by', models.ForeignKey(db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_updated_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='updated_by',
            field=models.ForeignKey(db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
