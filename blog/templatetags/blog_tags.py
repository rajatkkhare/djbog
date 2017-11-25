from django import template
from django.db.models import Case
from django.db.models import Count
from django.db.models import When
from django.utils import timezone
from blog.models import Category, Post

register = template.Library()


@register.simple_tag
def get_categories(status):
    return Category.objects.filter(status=status, post__status='P').annotate(post_count=Count('post')).exclude(
        post_count=0).order_by('-id').order_by('-post_count')


@register.simple_tag
def most_viewed(limit):
    today = timezone.now()
    thirty_days_ago = today - timezone.timedelta(days=30)
    return Post.objects.filter(status='P', created_at__gt=thirty_days_ago).annotate(
        comments=Count(Case(When(comment__status='A', comment__parent=None, then=1)))).order_by('-views')[:limit]


@register.simple_tag
def suggested_post(limit):
    today = timezone.now()
    thirty_days_ago = today - timezone.timedelta(days=30)
    return Post.objects.filter(status='P', created_at__gt=thirty_days_ago).annotate(
        comments=Count(Case(When(comment__status='A', comment__parent=None, then=1)))).order_by('?')[:limit]


@register.inclusion_tag('layouts/message.html')
def show_messages(messages):
    return {'messages': messages}
