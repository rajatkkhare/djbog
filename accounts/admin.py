from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from accounts.models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'accept': 'image/jpg,image/jpeg'}), required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), required=False)
    username = forms.CharField(required=False, help_text='Provide username or it will be generated automatically.')

    class Meta:
        model = User
        fields = ('email', 'is_staff')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            # user.send_registration_mail()
        return user


class UserChangeForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'accept': 'image/jpg,image/jpeg'}), required=False)
    remove_avatar = forms.BooleanField(label='Remove Avatar', required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), required=False)
    username = forms.CharField(required=False, help_text='Provide username or it will be generated automatically.')
    password = ReadOnlyPasswordHashField(
        help_text=("Raw passwords are not stored, so there is no way to see "
                   "this user's password, but you can change the password "
                   "using <a href=\"../password/\"><strong>this form</strong></a>."))

    class Meta:
        model = User
        fields = ('email', 'password', 'is_staff', 'is_active', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        if self.cleaned_data.get('remove_avatar'):
            user.avatar = None
            user.delete_avatar(user._current_avatar)
        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'username', 'get_full_name', 'date_joined', 'is_superuser', 'is_staff', 'is_active')
    list_editable = ['is_active']
    list_filter = ('is_active', 'is_staff')
    readonly_fields = ('user_avatar', 'last_login')
    list_per_page = 15
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username', 'is_active')}),
        ('Personal info', {'fields': (('first_name', 'last_name'), 'bio', 'avatar',
                                      ('user_avatar', 'remove_avatar'), 'last_login')}),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        })
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'fields': ('email', 'password1', 'password2', 'username', 'is_active')}),
        ('Personal info', {'fields': (('first_name', 'last_name'), 'bio', 'avatar')}),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        })
    )
    search_fields = ('email', '^username')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(User, UserAdmin)
