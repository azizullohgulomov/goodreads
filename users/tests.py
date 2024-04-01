from django.contrib.auth import get_user
from django.test import TestCase
from users.models import CustomUser
from django.urls import reverse

class RegistrationTestCase(TestCase):
    def test_user_account_is_created(self):
        self.client.post(
            reverse("users:register"),
            data={
                "username": "azizullohgulomov",
                "first_name": "Azizulloh",
                "last_name": "Gulomov",
                "email": "azizullohgulomov@gmail.com",
                "password": "12345678"
            }
        )

        user = CustomUser.objects.get(username="azizullohgulomov")

        self.assertEqual(user.first_name, "Azizulloh")
        self.assertEqual(user.last_name, "Gulomov")
        self.assertEqual(user.email, "azizullohgulomov@gmail.com")
        self.assertNotEqual(user.password, "12345678")
        self.assertTrue(user.check_password("12345678"))

    def test_required_fields(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "first_name": "Azizulloh",
                "email": "azizullohgulomov@gmail.com"
            }
        )

        user_count = CustomUser.objects.count()

        self.assertEqual(user_count, 0)
        self.assertFormError(response, "form", "username", "This field is required.")
        self.assertFormError(response, "form", "password", "This field is required.")


    def test_invalid_email(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "username": "azizullohgulomov",
                "first_name": "Azizulloh",
                "last_name": "Gulomov",
                "email": "invalid-email",
                "password": "12345678"
            }
        )

        user_count = CustomUser.objects.count()

        self.assertEqual(user_count, 0)
        self.assertFormError(response, "form", "email", "Enter a valid email address.")


    def test_unique_username(self):
        user = CustomUser.objects.create(username="azizullohgulomov", first_name="Azizulloh")
        user.set_password("12345678")
        user.save()


        response = self.client.post(
            reverse("users:register"),
            data={
                "username": "azizullohgulomov",
                "first_name": "Azizulloh",
                "last_name": "Gulomov",
                "email": "azizullohgulomov@gmail.com",
                "password": "12345678"
            }
        )

        user_count = CustomUser.objects.count()
        self.assertEqual(user_count, 1)

        self.assertFormError(response, "form", "username", "A user with that username already exists.")


class LoginTestCase(TestCase):
    def setUp(self):
        self.db_user = CustomUser.objects.create(username="azizullohgulomov", first_name="Azizulloh")
        self.db_user.set_password("12345678")
        self.db_user.save()

    def test_successful_login(self):
        self.client.post(
            reverse("users:login"),
            data={
                "username": "azizullohgulomov",
                "password": "12345678"
            }
        )

        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_wrong_credentials(self):
        self.client.post(
            reverse("users:login"),
            data={
                "username": "wrong-username",
                "password": "12345678"
            }
        )

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        self.client.post(
            reverse("users:login"),
            data={
                "username": "azizullohgulomov",
                "password": "wrong-password"
            }
        )

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_logout(self):
        db_user = CustomUser.objects.create(username="azizullohgulomov", first_name="Azizulloh")
        db_user.set_password("12345678")
        db_user.save()

        self.client.login(username="azizullohgulomov", password="12345678")

        self.client.get(reverse("users:logout"))

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)


class ProfileTestCase(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse("users:profile"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:login") + "?next=/users/profile/")

    def test_profile_details(self):
        user = CustomUser.objects.create(
            username="azizullohgulomov", first_name="Azizulloh", last_name="Gulomov", email="azizullohgulomov@gmail.com"
        )
        user.set_password("12345678")
        user.save()

        self.client.login(username="azizullohgulomov", password="12345678")

        response = self.client.get(reverse("users:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.username)
        self.assertContains(response, user.first_name)
        self.assertContains(response, user.last_name)
        self.assertContains(response, user.email)

    def test_update_profile(self):
        user = CustomUser.objects.create(
            username="azizullohgulomov", first_name="Azizulloh", last_name="Gulomov", email="azizullohgulomov@gmail.com"
        )
        user.set_password("12345678")
        user.save()

        self.client.login(username="azizullohgulomov", password="12345678")

        response = self.client.post(
            reverse("users:profile-edit"),
            data={
                "username": "azizullohgulomov",
                "first_name": "Azizulloh",
                "last_name": "Gulomovvv",
                "email": "azizullohgulomovvv@gmail.com"
            }
        )
        user.refresh_from_db()

        self.assertEqual(user.last_name, "Gulomovvv")
        self.assertEqual(user.email, "azizullohgulomovvv@gmail.com")
        self.assertEqual(response.url, reverse("users:profile"))
