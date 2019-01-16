from django.test import TestCase
from django.test.utils import override_settings

from .tasks import sample_celery_command


class AddTestCase(TestCase):

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       CELERY_BROKER_BACKEND='memory')
    def test_test_celery_command(self):
        result = sample_celery_command.delay(1, 2)
        self.assertEqual(result.get(), 3)
        self.assertTrue(result.successful())
