from blog.models import Category, Comment, Post
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, UpdateView)

from .forms import CommentForm, PostForm

User = get_user_model()


def index(request):
    # Получаем список всех объектов с сортировкой по дате публикации.
    posts = Post.objects.select_related('category', 'location').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).order_by('-pub_date')
    # Создаём объект пагинатора с количеством 10 записей на страницу.
    paginator = Paginator(posts, 10)
    # Получаем из запроса значение параметра page.
    page_number = request.GET.get('page')
    # Получаем запрошенную страницу пагинатора.
    # Если параметра page нет в запросе или его значение не приводится к числу,
    # вернётся первая страница.
    page_obj = paginator.get_page(page_number)
    # Вместо полного списка объектов передаём в контекст
    # объект страницы пагинатора
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author').filter(
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
    categories = get_object_or_404(
        Category.objects.values('title', 'description'),
        slug=category_slug
    )
    # Получаем список всех объектов с сортировкой по дате публикации.
    posts = get_list_or_404(
        Post.objects.only(
            'pub_date',
            'title',
            'location',
            'author',
            'text',
            'category__slug',
            'category__title',
        ).filter(
            category__slug=category_slug,
            is_published=True,
            pub_date__lte=timezone.now(),
        ).order_by('-pub_date'),
        category__is_published=True
    )
    # Создаём объект пагинатора с количеством 10 записей на страницу.
    paginator = Paginator(posts, 10)
    # Получаем из запроса значение параметра page.
    page_number = request.GET.get('page')
    # Получаем запрошенную страницу пагинатора.
    # Если параметра page нет в запросе или его значение не приводится к числу,
    # вернётся первая страница.
    page_obj = paginator.get_page(page_number)
    # Вместо полного списка объектов передаём в контекст
    # объект страницы пагинатора
    context = {
        'page_obj': page_obj,
        'category': categories,
    }
    return render(request, 'blog/category.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    # Указываем модель, с которой работает CBV...
    model = Post
    # Указываем поля, которые должны быть в форме:
    form_class = PostForm
    # Явным образом указываем шаблон:
    template_name = 'blog/create.html'
    # Указываем namespace:name страницы, куда будет перенаправлен пользователь

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.author})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:post_detail')

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )

    def dispatch(self, request, *args, **kwargs):
        # При получении объекта не указываем автора.
        # Результат сохраняем в переменную.
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        # Сверяем автора объекта и пользователя из запроса.
        if instance.author != request.user:
            # Здесь может быть как вызов ошибки,
            # так и редирект на нужную страницу.
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        # Если объект был найден, то вызываем родительский метод,
        # чтобы работа CBV продолжилась.
        return super().dispatch(request, *args, **kwargs)


@login_required
def add_comment(request, pk):
    # Получаем объект поста или выбрасываем 404 ошибку.
    post = get_object_or_404(Post, pk=pk)
    # Функция должна обрабатывать только POST-запросы.
    form = CommentForm(request.POST)
    if form.is_valid():
        # Создаём объект комментария, но не сохраняем его в БД.
        comment = form.save(commit=False)
        # В поле author передаём объект автора комментария.
        comment.author = request.user
        # В поле comment передаём объект поста.
        comment.post = post
        # Сохраняем объект в БД.
        comment.save()
    # Перенаправляем пользователя назад, на страницу поста.
    return redirect('blog:post_detail', pk=pk)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
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
        # При получении объекта не указываем автора.
        # Результат сохраняем в переменную.
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        # Сверяем автора объекта и пользователя из запроса.
        if instance.author != request.user:
            # Здесь может быть как вызов ошибки,
            # так и редирект на нужную страницу.
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
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
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(
            Comment, pk=kwargs['comment_id'], author=request.user
        )
        # Если объект был найден, то вызываем родительский метод,
        # чтобы работа CBV продолжилась.
        return super().dispatch(request, *args, **kwargs)


def profile_detail(request, username):
    """Отображение страницы пользователя"""
    profile = User.objects.get(username=username)
    post_list = Post.objects.filter(
        author__username=username
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
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