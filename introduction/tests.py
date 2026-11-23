from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import CSRF_user_tbl


class CSRFLabLoginTests(TestCase):
    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username="csrf-test-user", password="test-password"
            )
        )
        self.login_url = reverse("csrf_lab_login")
        self.password = "CSRF-lab-password"
        self.lab_user = CSRF_user_tbl(username="csrf-lab-user")
        self.lab_user.set_password(self.password)
        self.lab_user.save()

    def test_password_is_stored_with_django_password_hasher(self):
        self.lab_user.refresh_from_db()

        self.assertNotEqual(self.lab_user.password, self.password)
        self.assertTrue(self.lab_user.check_password(self.password))

    def test_valid_credentials_set_authentication_cookie(self):
        response = self.client.post(
            self.login_url,
            {"username": self.lab_user.username, "password": self.password},
        )

        self.assertRedirects(
            response,
            "/mitre/9/lab/transaction",
            fetch_redirect_response=False,
        )
        self.assertIn("auth_cookiee", response.cookies)

    def test_wrong_credentials_do_not_set_authentication_cookie(self):
        response = self.client.post(
            self.login_url,
            {"username": self.lab_user.username, "password": "wrong-password"},
        )

        self.assertRedirects(response, self.login_url, fetch_redirect_response=False)
        self.assertNotIn("auth_cookiee", response.cookies)

    def test_missing_credentials_do_not_set_authentication_cookie(self):
        response = self.client.post(self.login_url, {})

        self.assertRedirects(response, self.login_url, fetch_redirect_response=False)
        self.assertNotIn("auth_cookiee", response.cookies)

    def test_unknown_credentials_do_not_set_authentication_cookie(self):
        response = self.client.post(
            self.login_url,
            {"username": "unknown-user", "password": self.password},
        )

        self.assertRedirects(response, self.login_url, fetch_redirect_response=False)
        self.assertNotIn("auth_cookiee", response.cookies)
