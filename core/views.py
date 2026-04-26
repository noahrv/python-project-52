from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, redirect_to_login
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
    LabelForm,
    StatusForm,
    TaskForm,
)
from .models import Label, Status, Task


class HomeView(TemplateView):
    template_name = "core/home.html"


class UserListView(ListView):
    model = User
    template_name = "core/user_list.html"
    context_object_name = "users"


class UserCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "core/user_form.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        messages.success(self.request, "Пользователь успешно зарегистрирован")
        return super().form_valid(form)


class UserUpdateView(UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = "core/user_form.html"
    success_url = reverse_lazy("user_list")

    def dispatch(self, request, *args, **kwargs):
        if self.get_object() != request.user:
            messages.error(request, "У вас нет прав для изменения пользователя")
            return redirect("user_list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Пользователь успешно изменен")
        return super().form_valid(form)


class UserDeleteView(SuccessMessageMixin, DeleteView):
    model = User
    template_name = "core/user_confirm_delete.html"
    success_url = reverse_lazy("user_list")
    success_message = "Пользователь успешно удален"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object() != request.user:
            messages.error(request, "У вас нет прав для удаления пользователя")
            return redirect("user_list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = self.get_object()
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Невозможно удалить пользователя, "
                "потому что он связан с задачами",
            ),
            return redirect(self.success_url)


class UserLoginView(LoginView):
    template_name = "core/login.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        messages.success(self.request, "Вы залогинены")
        return super().form_valid(form)


class UserLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Вы разлогинены")
        return redirect("home")


class StatusListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = "core/status_list.html"
    context_object_name = "statuses"


class StatusCreateView(LoginRequiredMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = "core/status_form.html"
    success_url = reverse_lazy("status_list")

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно создан")
        return super().form_valid(form)


class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = "core/status_form.html"
    success_url = reverse_lazy("status_list")

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно изменен")
        return super().form_valid(form)


class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status
    template_name = "core/status_confirm_delete.html"
    success_url = reverse_lazy("status_list")

    def form_valid(self, form):
        self.object = self.get_object()

        if self.object.tasks.exists():
            messages.error(
                self.request,
                "Невозможно удалить статус, потому что он используется",
            )
            return redirect("status_list")

        messages.success(self.request, "Статус успешно удален")
        return super().form_valid(form)


class LabelListView(LoginRequiredMixin, ListView):
    model = Label
    template_name = "core/label_list.html"
    context_object_name = "labels"


class LabelCreateView(LoginRequiredMixin, CreateView):
    model = Label
    form_class = LabelForm
    template_name = "core/label_form.html"
    success_url = reverse_lazy("label_list")

    def form_valid(self, form):
        messages.success(self.request, "Метка успешно создана")
        return super().form_valid(form)


class LabelUpdateView(LoginRequiredMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = "core/label_form.html"
    success_url = reverse_lazy("label_list")

    def form_valid(self, form):
        messages.success(self.request, "Метка успешно изменена")
        return super().form_valid(form)


class LabelDeleteView(LoginRequiredMixin, DeleteView):
    model = Label
    template_name = "core/label_confirm_delete.html"
    success_url = reverse_lazy("label_list")

    def form_valid(self, form):
        self.object = self.get_object()

        if self.object.tasks.exists():
            messages.error(
                self.request,
                "Невозможно удалить метку, потому что она используется",
            )
            return redirect("label_list")

        messages.success(self.request, "Метка успешно удалена")
        return super().form_valid(form)


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "core/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        queryset = Task.objects.select_related(
            "status",
            "author",
            "executor",
        ).prefetch_related("labels")

        status_id = self.request.GET.get("status")
        executor_id = self.request.GET.get("executor")
        label_id = self.request.GET.get("label")
        self_tasks = self.request.GET.get("self_tasks")

        if status_id:
            queryset = queryset.filter(status_id=status_id)

        if executor_id:
            queryset = queryset.filter(executor_id=executor_id)

        if label_id:
            queryset = queryset.filter(labels__id=label_id)

        if self_tasks:
            queryset = queryset.filter(author=self.request.user)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Status.objects.all()
        context["executors"] = User.objects.all()
        context["labels"] = Label.objects.all()
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "core/task_detail.html"
    context_object_name = "task"
    queryset = Task.objects.select_related(
        "status",
        "author",
        "executor",
    ).prefetch_related("labels")


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "core/task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Задача успешно создана")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "core/task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        messages.success(self.request, "Задача успешно изменена")
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "core/task_confirm_delete.html"
    success_url = reverse_lazy("task_list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(), self.get_login_url()
            )

        task = self.get_object()
        if task.author != request.user:
            messages.error(request, "Задачу может удалить только ее автор")
            return redirect("task_list")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Задача успешно удалена")
        return super().form_valid(form)
