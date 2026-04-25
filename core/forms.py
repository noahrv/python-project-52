from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Status


class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        'duplicate_username': 'Пользователь с таким именем уже существует',
    }

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

    def clean_name(self):
        name = self.cleaned_data['name']
        queryset = Status.objects.filter(name=name)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError('Статус с таким именем уже существует')

        return name