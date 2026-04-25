from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Status


class StatusCRUDTest(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        self.user.set_password('pass123')
        self.user.save()

        self.status = Status.objects.create(name='новый')

    def test_status_list_requires_login(self):
        response = self.client.get(reverse('status_list'))
        self.assertRedirects(response, f'/login/?next={reverse("status_list")}')

    def test_create_status(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(reverse('status_create'), {'name': 'в работе'})
        self.assertRedirects(response, reverse('status_list'))
        self.assertTrue(Status.objects.filter(name='в работе').exists())
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Статус успешно создан' in str(m) for m in messages))

    def test_update_status(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(reverse('status_update', args=[self.status.pk]), {'name': 'на тестировании'})
        self.assertRedirects(response, reverse('status_list'))
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'на тестировании')
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Статус успешно изменен' in str(m) for m in messages))

    def test_delete_status(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(reverse('status_delete', args=[self.status.pk]))
        self.assertRedirects(response, reverse('status_list'))
        self.assertFalse(Status.objects.filter(pk=self.status.pk).exists())
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Статус успешно удален' in str(m) for m in messages))

    def test_access_control_for_anonymous(self):
        urls = [
            reverse('status_create'),
            reverse('status_update', args=[self.status.pk]),
            reverse('status_delete', args=[self.status.pk]),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f'/login/?next={url}')