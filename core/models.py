from django.conf import settings
from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name='tasks',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_tasks',
    )
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='assigned_tasks',
        null=True,
        blank=True,
    )
    labels = models.ManyToManyField(
        Label,
        related_name='tasks',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
