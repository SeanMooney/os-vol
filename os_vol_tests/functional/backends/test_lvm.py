# -*- coding: utf-8 -*-
import fixtures
from oslo_utils import units

from os_vol.backends import lvm
from os_vol_tests import base_test


class TestLVMFatBackend(base_test.OSVTestCase):

    def setUp(self):
        super().setUp()
        self.tempdir = self.useFixture(fixtures.TempDir())
        # TODO(sean): create the volume group on a loopback file
        # in the tempdir.
        self.pool_name = 'nova'
        self.backend = lvm.LVMFatPool(self.tempdir.path, self.pool_name)

    def test_get_vg_info(self):
        vg_info = self.backend.get_vg_info()
        self.assertEqual(self.pool_name, vg_info.name)
        self.assertGreater(vg_info.size, 0)
        self.assertIsInstance(vg_info, lvm.VGS)

    def test_ensure_vg_exists(self):
        vg_info = self.backend._ensure_vg_exists()
        self.assertIsNotNone(vg_info)
        self.assertIsInstance(vg_info, lvm.VGS)

    def test_used_space(self):
        self.assertEqual(0, self.backend.used_space)

    def test_free_space(self):
        self.assertGreater(self.backend.free_space, 0)

    def test_create_volume(self):
        size = 64 * units.Mi
        name = 'test'
        self.assertEqual(0, self.backend.used_space)
        volume = self.backend.create_volume(size, name)
        self.addCleanup(self.backend.delete_volume, volume)
        self.assertIsNotNone(volume)
        self.assertEqual(name, volume.name)
        self.assertEqual(size, volume.size)
        self.assertEqual(64, self.backend.used_space)

    def test_delete_volume(self):
        size = 64 * units.Mi
        name = 'test'
        volume = self.backend.create_volume(size, name)
        self.assertEqual(64, self.backend.used_space)
        self.backend.delete_volume(volume)
        self.assertEqual(0, self.backend.used_space)
        self.assertEqual(self.backend.capacity, self.backend.free_space)
