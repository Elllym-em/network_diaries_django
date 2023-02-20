import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Follow, Comment, Group, Post

User = get_user_model()

SECOND_PAGE_POSTS = 3
TEST_POSTS = settings.PAGINATOR + SECOND_PAGE_POSTS
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded
        )
        cls.templates_pages = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ): 'posts/profile.html',
            reverse('posts:create'): 'posts/create_and_edit_post.html',
            reverse(
                'posts:edit',
                kwargs={'post_id': cls.post.id}
            ): 'posts/create_and_edit_post.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        for reverse_name, template in self.templates_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.pk, self.post.id)
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.image, self.post.image)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.group)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.pk, self.post.id)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.group.title, self.group.title)
        self.assertEqual(
            first_object.group.description,
            self.group.description
        )
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.image, self.post.image)
        self.assertEqual(first_object.text, self.post.text)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.pk, self.post.id)
        self.assertEqual(first_object.group.title, self.group.title)
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.image, self.post.image)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.group)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(
            response.context.get('post').author,
            self.user)
        self.assertEqual(response.context.get('post').image, self.post.image)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').pk, self.post.id)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(reverse(
            'posts:edit',
            kwargs={'post_id': self.post.id}))
        Post.objects.filter(pk=1)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_comment_post_auth_client(self):
        """Комментировать пост может только авторизованный пользователь."""
        post = Post.objects.get(pk=self.post.id)
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария',
        }
        response = self.client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/')
        self.assertFalse(post.comment.filter(text=form_data['text']).exists())
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_post_group_in_correct_group(self):
        """Пост не попал в некорректную группу."""
        new_group = Group.objects.create(
            title='Новая группа',
            slug='new-slug')
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': new_group.slug}))
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_cache_index(self):
        """Проверка работы кэша."""
        response_old = self.client.get(reverse('posts:index'))
        old_list = response_old.content
        Post.objects.all().delete()
        response = self.client.get(reverse('posts:index'))
        new_list = response.content
        self.assertEqual(old_list, new_list)

    def test_follow_unfollow(self):
        new_user = User.objects.create_user(username='NewUser')
        authorized_new_client = Client()
        authorized_new_client.force_login(new_user)
        user_author = User.objects.create_user(username='Author')
        post = Post.objects.create(
            author=user_author,
            text='Новый текст',
        )
        Follow.objects.create(user=self.user, author=post.author)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        response_2 = authorized_new_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertIn(post, response.context['page_obj'])
        self.assertEqual(len(response_2.context['page_obj']), 0)
        self.assertNotIn(post, response_2.context['page_obj'])
        Follow.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
        self.assertNotIn(post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = []
        for i in range(TEST_POSTS):
            cls.posts.append(Post(
                text='Тестовый текст',
                author=cls.user,
                group=cls.group,)
            )
        Post.objects.bulk_create(cls.posts)

    def test_on_page_contains_correct_amount_records(self):
        """На странице отображается нужное количство записей posts."""
        pages = {
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
        }
        for reverse_name in pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), settings.PAGINATOR)
                response_2 = self.client.get((reverse_name) + '?page=2')
                self.assertEqual(
                    len(response_2.context['page_obj']), SECOND_PAGE_POSTS)
