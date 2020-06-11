#!/usr/bin/env python

"""
Adapted from django-contrib-comments, which itself was adapted from django-constance.
"""

import os
import sys
import django

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
sys.path[0:0] = [here, parent]

sys.path.append('./testapp')

from django.test.runner import DiscoverRunner

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')


def main(test_labels=None):
    django.setup()
    runner = DiscoverRunner(failfast=True, verbosity=1)
    failures = runner.run_tests(test_labels or ['testapp'], interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    test_labels = None
    if len(sys.argv) > 1:
        test_labels = sys.argv[1:]
    main(test_labels)
