from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Case, IntegerField
from django.db.models import Count
from django.db.models import When
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from blog.forms import CreateBlogForm
from blog.models import Post, Comment


def index(request):
    posts = Post.objects.filter(status='P', category__status='A').annotate(
        comments=Count(Case(When(comment__status='A', comment__parent=None, then=1)))).order_by('-created_at')[:6]
    return render(request, 'blog/index.html', {'posts': posts})


def search(request):
    q = request.GET.get('q', '')
    posts = Post.objects.annotate(relevance=Case(When(title__istartswith=q, then=10),
                                                 When(title__icontains=q, then=5), default=0,
                                                 output_field=IntegerField()))\
        .filter(status='P', category__status='A', relevance__gt=0).order_by('-relevance')
    return render(request, 'blog/index.html', {'posts': posts})


def details(request, slug):
    post = get_object_or_404(Post, slug=slug, status='P', category__status='A')
    post._meta.get_field('updated_at').auto_now = False
    post.views = int(post.views or 0) + 1
    post.save()
    post._meta.get_field('updated_at').auto_now = True
    total_comments = Comment.objects.filter(post=post.id, parent=None, status='A').count()
    comments = Comment.objects.filter(post=post.id, parent=None, status='A').order_by('-id')
    return render(request, 'blog/blog-details.html', {'post': post, 'total_comments': total_comments, 'comments': comments})


def categories(request, slug):
    return HttpResponse(slug)


@login_required
def create(request):
    form = CreateBlogForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('account')
    return render(request, 'blog/blog-create.html', {'form': form})


@login_required
def edit(request, slug):
    post = get_object_or_404(Post, slug=slug, user=request.user, status__in=['D', 'P'], category__status='A')
    form = CreateBlogForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.updated_by = request.user
            form.save()
            return redirect('account')
    return render(request, 'blog/blog-edit.html', {'post': post, 'form': form})


@login_required
def delete(request):
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=request.POST.get('slug'),
                                 user=request.user, status__in=['D', 'P'], category__status='A')
        post.updated_by = request.user
        post.status = 'X'
        post.save()
        return JsonResponse(True, safe=False)
    else:
        return JsonResponse(False, safe=False)
