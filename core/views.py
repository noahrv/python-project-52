from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth import logout
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from .forms import CustomUserCreationForm, CustomUserChangeForm, StatusForm
from .models import Status


class HomeView(TemplateView):
    template_name = 'core/home.html'


class UserListView(ListView):
    model = User
    template_name = 'core/user_list.html'
    context_object_name = 'users'


class UserCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Пользователь успешно зарегистрирован')
        return super().form_valid(form)


class UserUpdateView(UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('user_list')

    def dispatch(self, request, *args, **kwargs):
        if self.get_object() != request.user:
            messages.error(request, 'У вас нет прав для изменения пользователя')
            return redirect('user_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Пользователь успешно изменен')
        return super().form_valid(form)


class UserDeleteView(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'core/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    success_message = 'Пользователь успешно удален'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object() != request.user:
            messages.error(request, 'У вас нет прав для удаления пользователя')
            return redirect('user_list')
        return super().dispatch(request, *args, **kwargs)


class UserLoginView(LoginView):
    template_name = 'core/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'Вы залогинены')
        return super().form_valid(form)


class UserLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Вы разлогинены')
        return redirect('home')


class StatusListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = 'core/status_list.html'
    context_object_name = 'statuses'


class StatusCreateView(LoginRequiredMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = 'core/status_form.html'
    success_url = reverse_lazy('status_list')

    def form_valid(self, form):
        messages.success(self.request, 'Статус успешно создан')
        return super().form_valid(form)


class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = 'core/status_form.html'
    success_url = reverse_lazy('status_list')

    def form_valid(self, form):
        messages.success(self.request, 'Статус успешно изменен')
        return super().form_valid(form)


class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status
    template_name = 'core/status_confirm_delete.html'
    success_url = reverse_lazy('status_list')

    def form_valid(self, form):
        self.object = self.get_object()

        if self.object.task_set.exists():
            messages.error(self.request, 'Невозможно удалить статус')
            return redirect('status_list')

        messages.success(self.request, 'Статус успешно удален')
        return super().form_valid(form)