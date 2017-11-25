from django import template

register = template.Library()


@register.filter(is_safe=True)
def banner_url(url, dimension):
    url = url.split('/')
    img = ('/{}' + url[-1]).format(dimension)
    url.pop()
    return '/'.join(url)+img


@register.filter
def to_int(value):
    return int(value or 0)
