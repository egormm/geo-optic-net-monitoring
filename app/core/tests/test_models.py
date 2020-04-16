from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase

from core import models


def sample_user(email='test@test.com', password='testPassword123'):
    """Create a sample user for testing"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is succesfull"""
        email = "test@test.com"
        password = "testPassword123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "test@TeSt.com"
        user = get_user_model().objects.create_user(email, "testPassword123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with empty email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "testPassword123")

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email="test@test.com",
            password="testPassword123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_box_str(self):
        """Test the box string representation"""
        box = models.Box.objects.create(
            user=sample_user(),
            name='Box on the tree',
            point=Point([100, 500])
        )
        self.assertEqual(str(box), box.name)
