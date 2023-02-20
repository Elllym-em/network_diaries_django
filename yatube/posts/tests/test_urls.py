from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.not_author = User.objects.create_user(username='NotAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.tamplates = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            '/create/': 'posts/create_and_edit_post.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_and_edit_post.html',
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_no_author = Client()
        self.authorized_no_author.force_login(self.not_author)

    def test_post_url_exists_at_desired_client_location(self):
        """Проверка статус-кодов страниц по разным типам клиентов и случаев."""
        address_all = [
            ('/', self.client, HTTPStatus.OK),
            (f'/group/{self.group.slug}/', self.client, HTTPStatus.OK),
            (f'/profile/{self.user.username}/', self.client, HTTPStatus.OK),
            (f'/posts/{self.post.id}/', self.client, HTTPStatus.OK),
            (
                f'/posts/{self.post.id}/edit/',
                self.authorized_client,
                HTTPStatus.OK
            ),
            ('/create/', self.authorized_no_author, HTTPStatus.OK),
            (
                f'/posts/{self.post.id}/edit/',
                self.authorized_no_author,
                HTTPStatus.FOUND
            ),
            (f'/posts/{self.post.id}/edit/', self.client, HTTPStatus.FOUND),
            ('/create/', self.client, HTTPStatus.FOUND),
            ('/unexisting_page/', self.client, HTTPStatus.NOT_FOUND),
        ]
        for url, client, page_status in address_all:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, page_status)

    def test_create_post_url_redirect_anonymous_on_auth_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_post_edit_url_redirect_anonymous_on_auth_login(self):
        """Страница по адресу /posts/<int:post_id>/edit/
        перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get(f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/edit/')

    def test_all_url_uses_correct_template(self):
        """Проверка шаблонов для адресов /posts/."""
        for url, template in self.tamplates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
