from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()

POSTS_PER_PAGE = 10


def pagination(request, posts):
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    """Главная страница"""
    posts = Post.objects.select_related('category', 'location').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    page_obj = pagination(request, posts)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, pk):
    """Страница поста"""
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        pk=pk
    )
    if post.author != request.user:
        post = get_object_or_404(
            Post.objects.select_related(
                'category', 'location', 'author'
            ).filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            ),
            pk=pk
        )
    post_comments = post.comments.select_related('author')
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post_comments,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница категории"""
    categories = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    posts = Post.objects.select_related(
        'location', 'author', 'category'
    ).filter(
        category__slug=category_slug,
        is_published=True,
        pub_date__lte=timezone.now(),
    )
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
        'category': categories,
    }
    return render(request, 'blog/category.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста"""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.author})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование поста"""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if request.user != post.author:
            return redirect('blog:post_detail', pk=post.pk)
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление поста"""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if request.user != post.author:
            return redirect('blog:post_detail', pk=post.pk)
        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария"""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comments.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        posts = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = posts
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирования комментария"""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление комментария"""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def profile_detail(request, username):
    """Отображение страницы пользователя"""
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(
        author__username=username
    )
    page_obj = pagination(request, post_list)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя"""
    model = User
    fields = ('username', 'first_name', 'last_name', 'email')
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})
