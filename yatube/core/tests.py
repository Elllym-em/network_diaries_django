from django.test import TestCase


class CoreURLTest(TestCase):
    def test_404_uses_correct_template(self):
        """Проверка отдачи кастомного шаблона 404"""
        response = self.client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
