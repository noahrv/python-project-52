from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Label, Status, Task

TEST_USER_PASSWORD = "testpass123"


class TaskCrudTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author",
            password=TEST_USER_PASSWORD,
        )
        self.other_user = User.objects.create_user(
            username="other",
            password=TEST_USER_PASSWORD,
        )
        self.status = Status.objects.create(name="Новый")
        self.label = Label.objects.create(name="bug")

    def test_login_required_for_task_list(self):
        response = self.client.get(reverse("task_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_create_task(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("task_create"),
            {
                "name": "Первая задача",
                "description": "Описание задачи",
                "status": self.status.id,
                "executor": self.other_user.id,
                "labels": [self.label.id],
            },
        )

        self.assertRedirects(response, reverse("task_list"))
        task = Task.objects.get(name="Первая задача")
        self.assertEqual(task.author, self.author)
        self.assertEqual(task.executor, self.other_user)
        self.assertEqual(task.description, "Описание задачи")
        self.assertEqual(list(task.labels.all()), [self.label])

    def test_update_task(self):
        task = Task.objects.create(
            name="Старое имя",
            description="Старое описание",
            status=self.status,
            author=self.author,
        )
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("task_update", kwargs={"pk": task.pk}),
            {
                "name": "Новое имя",
                "description": "Новое описание",
                "status": self.status.id,
                "executor": self.other_user.id,
                "labels": [self.label.id],
            },
        )

        self.assertRedirects(response, reverse("task_list"))
        task.refresh_from_db()
        self.assertEqual(task.name, "Новое имя")
        self.assertEqual(task.executor, self.other_user)

    def test_only_author_can_delete_task(self):
        task = Task.objects.create(
            name="Нельзя удалить",
            description="",
            status=self.status,
            author=self.author,
        )
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("task_delete", kwargs={"pk": task.pk})
        )

        self.assertRedirects(response, reverse("task_list"))
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_author_can_delete_task(self):
        task = Task.objects.create(
            name="Можно удалить",
            description="",
            status=self.status,
            author=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("task_delete", kwargs={"pk": task.pk})
        )

        self.assertRedirects(response, reverse("task_list"))
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_user_linked_with_task_cannot_be_deleted(self):
        Task.objects.create(
            name="Связанная задача",
            description="",
            status=self.status,
            author=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("user_delete", kwargs={"pk": self.author.pk})
        )

        self.assertRedirects(response, reverse("user_list"))
        self.assertTrue(User.objects.filter(pk=self.author.pk).exists())

    def test_task_name_must_be_unique(self):
        Task.objects.create(
            name="Дубликат",
            description="",
            status=self.status,
            author=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("task_create"),
            {
                "name": "Дубликат",
                "description": "",
                "status": self.status.id,
                "executor": "",
                "labels": [],
            },
        )

        self.assertContains(response, "уже существует")

    def test_filter_tasks_by_status(self):
        another_status = Status.objects.create(name="В работе")
        matching_task = Task.objects.create(
            name="Подходит по статусу",
            description="",
            status=self.status,
            author=self.author,
        )
        Task.objects.create(
            name="Не подходит по статусу",
            description="",
            status=another_status,
            author=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("task_list"),
            {"status": self.status.id},
        )

        self.assertContains(response, matching_task.name)
        self.assertNotContains(response, "Не подходит по статусу")

    def test_filter_tasks_by_executor(self):
        matching_task = Task.objects.create(
            name="Подходит по исполнителю",
            description="",
            status=self.status,
            author=self.author,
            executor=self.other_user,
        )
        Task.objects.create(
            name="Не подходит по исполнителю",
            description="",
            status=self.status,
            author=self.author,
            executor=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("task_list"),
            {"executor": self.other_user.id},
        )

        self.assertContains(response, matching_task.name)
        self.assertNotContains(response, "Не подходит по исполнителю")

    def test_filter_tasks_by_label(self):
        another_label = Label.objects.create(name="feature")
        matching_task = Task.objects.create(
            name="Подходит по метке",
            description="",
            status=self.status,
            author=self.author,
        )
        matching_task.labels.add(self.label)

        other_task = Task.objects.create(
            name="Не подходит по метке",
            description="",
            status=self.status,
            author=self.author,
        )
        other_task.labels.add(another_label)

        self.client.force_login(self.author)

        response = self.client.get(
            reverse("task_list"),
            {"label": self.label.id},
        )

        self.assertContains(response, matching_task.name)
        self.assertNotContains(response, other_task.name)

    def test_filter_only_self_tasks(self):
        matching_task = Task.objects.create(
            name="Моя задача",
            description="",
            status=self.status,
            author=self.author,
        )
        Task.objects.create(
            name="Чужая задача",
            description="",
            status=self.status,
            author=self.other_user,
        )
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("task_list"),
            {"self_tasks": "on"},
        )

        self.assertContains(response, matching_task.name)
        self.assertNotContains(response, "Чужая задача")

    def test_filter_tasks_by_status_executor_and_label(self):
        matching_task = Task.objects.create(
            name="Подходит по всем фильтрам",
            description="",
            status=self.status,
            author=self.author,
            executor=self.other_user,
        )
        matching_task.labels.add(self.label)

        Task.objects.create(
            name="Не подходит по исполнителю",
            description="",
            status=self.status,
            author=self.author,
            executor=self.author,
        )

        self.client.force_login(self.author)

        response = self.client.get(
            reverse("task_list"),
            {
                "status": self.status.id,
                "executor": self.other_user.id,
                "label": self.label.id,
            },
        )

        self.assertContains(response, matching_task.name)
        self.assertNotContains(response, "Не подходит по исполнителю")

    def test_create_status(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("status_create"),
            {"name": "Новый статус"},
        )

        self.assertRedirects(response, reverse("status_list"))
        self.assertTrue(Status.objects.filter(name="Новый статус").exists())

    def test_update_status(self):
        status = Status.objects.create(name="Старый")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("status_update", kwargs={"pk": status.pk}),
            {"name": "Готово"},
        )

        self.assertRedirects(response, reverse("status_list"))
        status.refresh_from_db()
        self.assertEqual(status.name, "Готово")

    def test_delete_status(self):
        status = Status.objects.create(name="Удаляемый")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("status_delete", kwargs={"pk": status.pk})
        )

        self.assertRedirects(response, reverse("status_list"))
        self.assertFalse(Status.objects.filter(pk=status.pk).exists())

    def test_cannot_delete_status_if_used(self):
        status = Status.objects.create(name="Используется")
        Task.objects.create(
            name="Связана",
            description="",
            status=status,
            author=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("status_delete", kwargs={"pk": status.pk})
        )

        self.assertRedirects(response, reverse("status_list"))
        self.assertTrue(Status.objects.filter(pk=status.pk).exists())

    def test_create_label(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("label_create"),
            {"name": "feature"},
        )

        self.assertRedirects(response, reverse("label_list"))
        self.assertTrue(Label.objects.filter(name="feature").exists())

    def test_update_label(self):
        label = Label.objects.create(name="old_label")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("label_update", kwargs={"pk": label.pk}),
            {"name": "feature"},
        )

        self.assertRedirects(response, reverse("label_list"))
        label.refresh_from_db()
        self.assertEqual(label.name, "feature")

    def test_delete_label(self):
        label = Label.objects.create(name="Удаляемая")
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("label_delete", kwargs={"pk": label.pk})
        )

        self.assertRedirects(response, reverse("label_list"))
        self.assertFalse(Label.objects.filter(pk=label.pk).exists())

    def test_cannot_delete_label_if_used(self):
        label = Label.objects.create(name="Используется")
        task = Task.objects.create(
            name="Связана",
            description="",
            status=self.status,
            author=self.author,
        )
        task.labels.add(label)

        self.client.force_login(self.author)

        response = self.client.post(
            reverse("label_delete", kwargs={"pk": label.pk})
        )

        self.assertRedirects(response, reverse("label_list"))
        self.assertTrue(Label.objects.filter(pk=label.pk).exists())

    def test_login_required_for_status_list(self):
        response = self.client.get(reverse("status_list"))
        self.assertEqual(response.status_code, 302)

    def test_login_required_for_label_list(self):
        response = self.client.get(reverse("label_list"))
        self.assertEqual(response.status_code, 302)
