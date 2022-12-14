from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase

from boards.views import board_topics, TopicListView
from boards.models import Board


class BoardTopicsTests(TestCase):
    def setUp(self) -> None:
        Board.objects.create(name='Django', description='Django Board.')

    def test_board_topics_view_success_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve('/boards/1/')
        # self.assertEqual(view.func, board_topics)
        self.assertEqual(view.func.view_class, TopicListView)

    def test_board_topics_view_contains_link_back_to_home_page(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse('home')
        self.assertContains(response, f'href="{homepage_url}"')

    def test_board_topics_view_contains_navigation_link(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        homepage_url = reverse('home')
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})

        response = self.client.get(board_topics_url)

        self.assertContains(response, f'href="{homepage_url}"')
        self.assertContains(response, f'href="{new_topic_url}"')
