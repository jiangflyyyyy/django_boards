from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase
from boards.models import Board, Topic, Post
from boards.views import PostUpdateView
from django.forms import ModelForm


class PostUpdatedViewTestCase(TestCase):
    def setUp(self) -> None:
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(username=self.username, password=self.password, email='john@doe.com')
        self.topic = Topic.objects.create(subject='Hello, world!', board=self.board, starter=user)
        self.post = Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=user)
        self.url = reverse('edit_post', kwargs={
            'pk': self.board.pk,
            'topic_pk': self.topic.pk,
            'post_pk': self.post.pk
        })


class LoginRequiredPostUpdateViewTests(PostUpdatedViewTestCase):
    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, f'{login_url}?next={self.url}')


class UnauthorizedPostUpdateViewTests(PostUpdatedViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        username = 'jane'
        password = '321'
        user = User.objects.create_user(username=username, password=password, email='jane@doe.com')
        self.client.login(username=username, password=password)
        self.response = self.client.get(self.url)

    def test_status_code(self):
        print(self.response.status_code)
        self.assertEquals(self.response.status_code, 404)


class PostUpdateViewTests(PostUpdatedViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_class(self):
        view = resolve('/boards/1/topics/1/posts/1/edit/')
        self.assertEqual(view.func.view_class, PostUpdateView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, ModelForm)

    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)


class SuccessfulPostUpdateViewTests(PostUpdatedViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'edited message.'})

    def test_redirection(self):
        topic_posts_url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertRedirects(self.response, topic_posts_url)

    def test_post_changed(self):
        self.post.refresh_from_db()
        self.assertEqual(self.post.message, 'edited message.')


class InvalidPostUpdateViewTests(PostUpdatedViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
