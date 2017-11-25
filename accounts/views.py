from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from accounts.forms import UserLoginForm, UserRegistrationForm, EditAccountForm
from blog.models import Post
from common.decorators.anonymous_required import anonymous_required

User = get_user_model()


@anonymous_required
def register_view(request, next_page):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = User(first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'], email=form.cleaned_data['email'])
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            user.send_registration_mail()
            login(request, authenticate(username=user.username, password=form.cleaned_data['password']))
            return redirect(request.POST.get('next') if request.POST.get('next') else next_page)
    return render(request, 'accounts/register.html', {'form': form})


@anonymous_required
def login_view(request, next_page):
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            login(request, authenticate(username=username, password=password))
            return redirect(request.POST.get('next') if request.POST.get('next') else next_page)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def user_account(request):
    user = request.user
    posts = Post.objects.filter(user=user, status__in=['D', 'P'], category__status='A').order_by('-updated_at')
    paginator = Paginator(posts, 10)
    try:
        posts = paginator.page(request.GET.get('page', 1))
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'accounts/account.html', {'user': user, 'posts': posts})


@login_required
def update_account(request):
    user = request.user
    form = EditAccountForm(request.POST or None, request.FILES or None, request=request)
    if request.method == 'POST':
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['username']
            user.avatar = form.cleaned_data['avatar']
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data.get('password'))
                login(request, authenticate(username=user.username, password=form.cleaned_data['password']))
            user.save()
            return redirect('account')
    return render(request, 'accounts/account-update.html', {'user': user, 'form': form})

