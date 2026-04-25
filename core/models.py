from django.db import models

class Status(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=100)
    status = models.ForeignKey('Status', on_delete=models.PROTECT, related_name='task_set')