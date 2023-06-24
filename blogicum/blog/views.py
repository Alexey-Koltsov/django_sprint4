from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DeleteView, DetailView
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy

from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.utils import timezone

from blog.models import Category, Post
from django.contrib.auth import get_user_model

from .forms import PostForm

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


def post_detail(request, id):
    posts = get_object_or_404(
        Post.objects.select_related('category', 'location').filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ),
        pk=id
    )
    context = {'post': posts}
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
    # после создания объекта:
    success_url = reverse_lazy('blog:profile')

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


def profile_detail(request, username):
    """Отображение страницы пользователя"""
    profile = User.objects.get(username=username)
    post_list = Post.objects.filter(author__username=username)
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
    success_url = reverse_lazy('blog:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})
