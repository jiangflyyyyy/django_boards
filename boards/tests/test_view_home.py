from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase

from boards.views import home, BoardListView
from boards.models import Board


class HomeTests(TestCase):
    def setUp(self) -> None:
        self.board = Board.objects.create(name='Django', description='Django Board.')
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        """
        测试请求URL后返回响应状态码
        :return:
        """
        self.assertEqual(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        """
        将浏览器发起请求的URL与urls.py中的列出的URL进行匹配
        :return:
        """
        view = resolve('/')
        # self.assertEqual(view.func, home)
        self.assertEqual(view.func.view_class, BoardListView)

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, f'href="{board_topics_url}"')
