from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Label, Status, Task


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        error_messages = {
            'username': {
                'unique': 'Пользователь с таким именем уже существует',
            },
        }


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Имя пользователя',
        }
        error_messages = {
            'username': {
                'unique': 'Пользователь с таким именем уже существует',
            },
        }


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']
        labels = {
            'name': 'Имя',
        }
        error_messages = {
            'name': {
                'unique': 'Статус с таким именем уже существует',
            },
        }


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name']
        labels = {
            'name': 'Имя',
        }
        error_messages = {
            'name': {
                'unique': 'Метка с таким именем уже существует',
            },
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'status', 'executor', 'labels']
        labels = {
            'name': 'Имя',
            'description': 'Описание',
            'status': 'Статус',
            'executor': 'Исполнитель',
            'labels': 'Метки',
        }
        error_messages = {
            'name': {
                'unique': 'Задача с таким именем уже существует',
            },
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }