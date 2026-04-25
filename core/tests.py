from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UserCRUDTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')

    def test_create_user(self):
        response = self.client.post(reverse('user_create'), {
            'username': 'newuser',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_update_user(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(reverse('user_update', args=[self.user.pk]), {
            'username': 'updateduser',
            'first_name': 'New',
            'last_name': 'Name'
        })
        self.assertRedirects(response, reverse('user_list'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_delete_user(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(reverse('user_delete', args=[self.user.pk]))
        self.assertRedirects(response, reverse('user_list'))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_login_logout(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'pass123'})
        self.assertRedirects(response, reverse('home'))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Вы залогинены' in str(m) for m in messages))

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Вы разлогинены' in str(m) for m in messages))