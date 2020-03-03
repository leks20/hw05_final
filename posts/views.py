from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count
from posts.models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm

User = get_user_model()


def index(request):
    post_list = Post.objects.select_related('author', 'group').order_by("-pub_date").annotate(
        comment_count=Count('comment'))

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "index.html", {
        'paginator': paginator,
        'page': page
        }
        )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).select_related('author').order_by(
        "-pub_date").annotate(comment_count=Count('comment'))

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "group.html", {
        'group': group,
        'paginator': paginator,
        'page': page
        }
        )


@login_required
def new_post(request):
    context = {
        'title': "Новая запись",
        'header': "Добавить запись",
        'button': "Добавить"
        }

    form = PostForm(
        request.POST or None,
        files=request.FILES or None
        )

    if request.method == "POST":
        if form.is_valid():
            my_post = form.save(commit=False)
            my_post.author = request.user
            my_post.save()
            return redirect("index")

        context['form'] = form
        return render(request, 'new.html', context)

    context['form'] = form
    return render(request, "new.html", context)


def profile(request, username):
    following = False
    follow_button = False

    profile = get_object_or_404(User, username=username)
    posts_profile = Post.objects.filter(author=profile).select_related(
        'group').order_by("-pub_date").annotate(comment_count=Count('comment'))
    posts_count = posts_profile.count()

    followers = Follow.objects.filter(author=profile).count
    following_authors = Follow.objects.filter(user=profile).count

    paginator = Paginator(posts_profile, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=profile).count():
            following = True
    if request.user != profile:
        follow_button = True

    return render(request, "profile.html", {
        'paginator': paginator,
        'page': page,
        'profile': profile,
        'posts_count': posts_count,
        'following': following,
        'follow_button': follow_button,
        'followers': followers,
        'following_authors': following_authors
        }
        )


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = Post.objects.select_related('author', 'group').annotate(
        comment_count=Count('comment')).get(pk=post_id)
    posts_count = Post.objects.filter(author=profile).count()

    comments = Comment.objects.filter(post=post).select_related(
        'author').order_by("-created").all()
    form = CommentForm()

    return render(request, "post.html", {
        'profile': profile,
        'post': post,
        'posts_count': posts_count,
        'comments': comments,
        'form': form,
        })


@login_required
def post_edit(request, username, post_id):
    context = {
        'title': "Редактировать запись",
        'header': "Редактировать запись",
        'button': "Сохранить"
        }
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    context['post'] = post

    if request.user != author:
        return redirect("post", username=username, post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
        )

    if request.method == "POST":
        if form.is_valid():
            post = form.save()
            return redirect("post", username=username, post_id=post_id)

        context['form'] = form
        return render(request, 'new.html', context)

    context['form'] = form
    return render(request, "new.html", context)


@login_required
def post_delete(request, username, post_id):
    author = User.objects.get(username=username)
    post = Post.objects.get(pk=post_id)

    if request.user != author:
        return redirect("post", username=username, post_id=post_id)

    post.delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile = get_object_or_404(User, username=username)
    comments = Comment.objects.filter(post=post).select_related('author').all()
    posts_count = Post.objects.filter(author=profile).count()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect("post", username=username, post_id=post_id)

        return render(request, 'post.html', {'form': form})

    form = CommentForm()
    return render(request, "post.html", {
        'form': form,
        'post': post,
        'profile': profile,
        'posts_count': posts_count,
        'comments': comments,
        })


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(
        author__following__user=request.user).select_related(
        'author', 'group').order_by("-pub_date").annotate(
        comment_count=Count('comment'))

    paginator = Paginator(posts_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "follow.html", {
        'paginator': paginator,
        'page': page,
    })


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    count = Follow.objects.filter(user=request.user, author=author).count()
    if request.user == author or count > 0:
        return redirect("profile", username=username)
    else:
        Follow.objects.create(user=request.user, author=author)
        return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    if request.user == author:
        return redirect("profile", username=username)
    else:
        following = Follow.objects.get(user=request.user, author=author)
        following.delete()
        return redirect("profile", username=username)
