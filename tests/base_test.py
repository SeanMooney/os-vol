# -*- coding: utf-8 -*-
# Copyright 2024 - 2024, Sean Mooney and the os-vol contributors
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest

import fixtures

LOG = logging.getLogger(__name__)


class TestPytest(unittest.TestCase):

    def test_framework_is_working(self) -> None:
        self.assertTrue(True)

    def test_import_worked(self) -> None:
        import os_vol
        self.assertIsNotNone(os_vol)


class OSVTestCase(unittest.TestCase):

    USE_LOG_FIXTURE = True

    def setUp(self):
        super().setUp()
        self.log_fixture = (
            self.useFixture(fixtures.FakeLogger())
            if self.USE_LOG_FIXTURE else None
        )

    def replace_log_fixture(self, log_level) -> None:
        self.log_fixture = self.useFixture(
            fixtures.FakeLogger(level=log_level))

    def useFixture(self, fixture: fixtures.Fixture) -> fixtures.Fixture:
        """Use a fixture in a test case.

        This method is a convenience method to use fixtures in a test case.
        It sets up the fixture and adds the cleanup to the test case.
        if the fixture is None, it will return None.

        :param fixture: The fixture to use.
        :returns: The fixture.
        """
        if fixture is None:
            return None
        fixture.setUp()
        self.addCleanup(fixture.cleanUp)
        return fixture


class TestOSV(OSVTestCase):

    def test_version(self) -> None:
        import os_vol
        self.assertIsNotNone(os_vol.__version__)
        self.assertNotEqual(os_vol.__version__, 'unknown')

    def test_log_fixture(self) -> None:
        self.assertIsNotNone(self.log_fixture)
        LOG.info('This is a test log message')
        self.assertIn('This is a test log message', self.log_fixture.output)
