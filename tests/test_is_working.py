from django.test import TestCase


class TestIsWorking(TestCase):
    def test_is_working(self):
        self.assertIsNone(None)