from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import Category, Post, Comment, CATEGORY_STATUS, POST_STATUS, COMMENT_STATUS


class CategoryForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea, required=False)
    status = forms.ChoiceField(choices=tuple([_ for _ in CATEGORY_STATUS if _[0] != "X"]))


class StatusListFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'status__exact'

    def lookups(self, request, model_admin):
        return tuple([_ for _ in CATEGORY_STATUS if _[0] != "X"])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value()).exclude(status='X')
        return queryset.exclude(status='X')


class CategoryAdmin(admin.ModelAdmin):
    fields = ('title', 'description', 'status')
    list_display = ('title', 'user', 'created_at', 'status')
    list_editable = ['status']
    list_filter = [StatusListFilter]
    actions = ['delete']
    form = CategoryForm

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.user = request.user
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False

    def delete(self, request, queryset):
        rows_updated = queryset.update(status='X', updated_by=request.user, updated_at=timezone.now())
        if rows_updated == 1:
            message_bit = "1 category"
        else:
            message_bit = "{} categories".format(rows_updated)
        self.message_user(request, "{} deleted successfully.".format(message_bit))
    delete.short_description = 'Delete'


class PostForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.filter(status='A'))
    body = forms.CharField(widget=forms.Textarea)
    banner = forms.ImageField(widget=forms.FileInput(attrs={'accept': 'image/jpg,image/jpeg'}))
    status = forms.ChoiceField(choices=tuple([_ for _ in POST_STATUS if _[0] != "X"]))

    # def clean_banner(self):
    #     banner = self.cleaned_data.get('banner')
    #     if not banner.name.endswith(".jpg"):
    #         raise forms.ValidationError("Only .jpg image accepted")
    #     return banner


class PostAdmin(admin.ModelAdmin):
    form = PostForm
    list_display = ('title', 'category', 'user', 'created_at', 'status')
    exclude = ('views', 'slug', 'user', 'updated_by')
    list_editable = ['status']
    readonly_fields = ('post_banner',)
    list_per_page = 15
    search_fields = ['title']

    def get_queryset(self, request):
        return Post.objects.exclude(status='X')

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.user = request.user
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return False


class CommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea)
    status = forms.ChoiceField(choices=tuple([_ for _ in COMMENT_STATUS if _[0] != "X"]))
    post = forms.ModelChoiceField(queryset=Post.objects.filter(status='P').order_by('-id'))


class CommentAdmin(admin.ModelAdmin):
    form = CommentForm
    fields = ('post', 'comment', 'status')
    list_display = ('comment', 'user', 'created_at', 'status')
    list_editable = ['status']
    list_per_page = 15

    def get_queryset(self, request):
        return Comment.objects.exclude(status='X')

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.user = request.user
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.readonly_fields = ['post']
        else:
            self.readonly_fields = ['']
        return super(CommentAdmin, self).get_form(request, obj, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.disable_action('delete_selected')
