from django import forms
from blog.models import Post, Category


class CreateBlogForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.filter(status='A'))

    class Meta:
        model = Post
        fields = ['title', 'short_description', 'body', 'banner', 'status', 'category']
