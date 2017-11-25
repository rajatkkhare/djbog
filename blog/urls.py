from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^search/$', views.search, name='search'),
    url(r'^new/$', views.create, name='create_blog'),
    url(r'^edit/(?P<slug>[\w-]+)/$', views.edit, name='edit_blog'),
    url(r'^delete/$', views.delete, name='delete_blog'),
    url(r'^(?P<slug>[\w-]+)/$', views.details, name='details'),
    url(r'^categories/(?P<slug>[\w-]+)/$', views.categories, name='categories'),
]
