# -*- coding: utf-8 -*-
# Copyright 2024 - 2024, Sean Mooney and the os-vol contributors
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest

LOG = logging.getLogger(__name__)


class TestPytest(unittest.TestCase):

    def test_framework_is_working(self):
        self.assertTrue(True)

    def test_import_worked(self):
        import os_vol
        self.assertIsNotNone(os_vol)
