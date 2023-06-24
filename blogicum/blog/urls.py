from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    # Путь к странице создания поста
    path('post/create', views.PostCreateView.as_view(), name='create_post'),
    # Путь к странице profile
    path('profile/<slug:username>/', views.profile_detail, name='profile'),
    # Путь к странице редактирования profile
    path('profile/<slug:username>/edit/', views.UserUpdateView.as_view(),
         name='edit_profile'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
]
