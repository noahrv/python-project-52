from django.contrib import admin

from .models import Label, Status, Task


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'author', 'executor')
    list_filter = ('status', 'labels')
