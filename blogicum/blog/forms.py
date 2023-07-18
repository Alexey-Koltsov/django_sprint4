from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Переопределяем модель пользователя и поля модели."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class PostForm(forms.ModelForm):
    """Форма для модели постов."""
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local',
                                                   'class': 'form-control'})
        }


class CommentForm(forms.ModelForm):
    """Форма для модели комментариев."""
    class Meta:
        model = Comment
        fields = ('text',)
