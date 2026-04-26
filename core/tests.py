from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Label, Status, Task


class TaskCrudTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='password')
        self.other_user = User.objects.create_user(
            username='other', password='password'
        )
        self.status = Status.objects.create(name='Новый')
        self.label = Label.objects.create(name='bug')

    def test_login_required_for_task_list(self):
        response = self.client.get(reverse('task_list'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_create_task(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse('task_create'),
            {
                'name': 'Первая задача',
                'description': 'Описание задачи',
                'status': self.status.id,
                'executor': self.other_user.id,
                'labels': [self.label.id],
            },
        )

        self.assertRedirects(response, reverse('task_list'))
        task = Task.objects.get(name='Первая задача')
        self.assertEqual(task.author, self.author)
        self.assertEqual(task.executor, self.other_user)
        self.assertEqual(task.description, 'Описание задачи')
        self.assertEqual(list(task.labels.all()), [self.label])

    def test_update_task(self):
        task = Task.objects.create(
            name='Старое имя',
            description='Старое описание',
            status=self.status,
            author=self.author,
        )
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse('task_update', kwargs={'pk': task.pk}),
            {
                'name': 'Новое имя',
                'description': 'Новое описание',
                'status': self.status.id,
                'executor': self.other_user.id,
                'labels': [self.label.id],
            },
        )

        self.assertRedirects(response, reverse('task_list'))
        task.refresh_from_db()
        self.assertEqual(task.name, 'Новое имя')
        self.assertEqual(task.executor, self.other_user)

    def test_only_author_can_delete_task(self):
        task = Task.objects.create(
            name='Нельзя удалить',
            description='',
            status=self.status,
            author=self.author,
        )
        self.client.force_login(self.other_user)

        response = self.client.post(reverse('task_delete', kwargs={'pk': task.pk}))

        self.assertRedirects(response, reverse('task_list'))
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_author_can_delete_task(self):
        task = Task.objects.create(
            name='Можно удалить',
            description='',
            status=self.status,
            author=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.post(reverse('task_delete', kwargs={'pk': task.pk}))

        self.assertRedirects(response, reverse('task_list'))
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_user_linked_with_task_cannot_be_deleted(self):
        Task.objects.create(
            name='Связанная задача',
            description='',
            status=self.status,
            author=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.post(
            reverse('user_delete', kwargs={'pk': self.author.pk})
        )

        self.assertRedirects(response, reverse('user_list'))
        self.assertTrue(User.objects.filter(pk=self.author.pk).exists())

    def test_task_name_must_be_unique(self):
        Task.objects.create(
            name='Дубликат',
            description='',
            status=self.status,
            author=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.post(
            reverse('task_create'),
            {
                'name': 'Дубликат',
                'description': '',
                'status': self.status.id,
                'executor': '',
                'labels': [],
            },
        )

        self.assertContains(response, 'уже существует')
