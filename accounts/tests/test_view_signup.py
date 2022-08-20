from django.test import TestCase
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.contrib.auth.models import User

from accounts.forms import SignUpForm
from accounts.views import signup


class SignUpTests(TestCase):
    def setUp(self) -> None:
        url = reverse('signup')
        self.response = self.client.get(url)

    def test_sign_up_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_sign_up_url_resolves_sign_up_view(self):
        view = resolve('/signup/')
        self.assertEqual(view.func, signup)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)

    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)


class SuccessfulSignUpTests(TestCase):
    def setUp(self) -> None:
        url = reverse('signup')
        data = {
            'username': 'zhangsan',
            'password1': 'abcd1234',
            'password2': 'abcd1234'
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')

    def test_redirection(self):
        self.assertRedirects(self.response, self.home_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.authenticated)


class InvalidSignUpTests(TestCase):
    def setUp(self) -> None:
        url = reverse('signi[')
        self.response = self.client.post(url, {})

    def test_sign_up_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        self.assertFalse(User.objects.exists())
