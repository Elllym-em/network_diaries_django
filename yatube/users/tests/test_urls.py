from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_url_exists_at_desired_location(self):
        """Проверка доступности адресов /users/
        для неавторизованных пользователей.
        """
        adress = ('/auth/signup/', '/auth/login/')
        for url in adress:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_url_uses_correct_template(self):
        """Проверка шаблонов для адресов /users/
        для неавторизованных пользователей.
        """
        templates = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
        }
        for url, template in templates.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)

    def test_auth_url_exists_at_desired_location(self):
        """Проверка доступности адресов /users/
        для авторизованных пользователей.
        """
        adress = (
            '/auth/password_change/',
            '/auth/password_change_done/',
            '/auth/logout/',
        )
        for url in adress:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_url_uses_correct_template(self):
        """Проверка шаблонов для адресов /users/
        для авторизованных пользователей.
        """
        templates = {
            '/auth/password_change/': 'users/password_change.html',
            '/auth/password_change_done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for url, template in templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
