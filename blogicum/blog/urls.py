from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # Путь к главной странице
    path('', views.index, name='index'),

    # Путь к странице создания поста
    path('post/create', views.PostCreateView.as_view(), name='create_post'),
    # Путь к странице поста
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    # Путь к странице редактирования поста
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    # Путь к странице удаления поста
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),

    # Путь к странице добавления комментария
    path('posts/<int:pk>/comment/', views.add_comment,
         name='add_comment'),
    # Путь к странице изменения комментария
    path('posts/<int:pk>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='delete_comment'),
    # Путь к странице удаления комментария
    path('posts/<int:pk>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),

    # Путь к странице profile
    path('profile/<slug:username>/', views.profile_detail, name='profile'),
    # Путь к странице редактирования profile
    path('profile/<slug:username>/edit/', views.UserUpdateView.as_view(),
         name='edit_profile'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
]
