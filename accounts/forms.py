from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from common.validators import validate_extension

User = get_user_model()


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('Incorrect username or password.', code='invalid')
                # raise forms.ValidationError({'username': ['This user does not exist.']}, code='invalid')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect Password', code='invalid')
            if not user.is_active:
                raise forms.ValidationError('Your account has been disabled.', code='invalid')
        return super(UserLoginForm, self).clean()


error_messages = {
    'max_length': 'Must not exceed %(limit_value)d characters',
    'min_length': 'Must be at least %(limit_value)d characters long'
}

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')


class UserRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=30, error_messages=error_messages, validators=[alphanumeric])
    last_name = forms.CharField(max_length=30, error_messages=error_messages, validators=[alphanumeric])
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, error_messages=error_messages)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use")
        return email

    def clean(self):
        cleaned_data = super(UserRegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError({'confirm_password': ['These passwords don\'t match']},
                                            code='invalid')
        return cleaned_data


class EditAccountForm(UserRegistrationForm):
    username = forms.CharField(max_length=10, error_messages=error_messages)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, error_messages=error_messages, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'accept': 'image/jpg,image/jpeg'}), validators=[validate_extension], required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EditAccountForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(id=self.request.user.id).exists():
            raise forms.ValidationError("Username already in use")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.request.user.id).exists():
            raise forms.ValidationError("Email already in use")
        return email

    def clean(self):
        cleaned_data = super(EditAccountForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError({'confirm_password': ['These passwords don\'t match']},
                                            code='invalid')
        return cleaned_data
