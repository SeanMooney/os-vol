# -*- coding: utf-8 -*-

import os

import fixtures

from os_vol.backends import flat_file
from os_vol_tests import base_test


class TestFlatFileBackend(base_test.OSVTestCase):
    def setUp(self):
        super().setUp()
        self.tempdir = self.useFixture(fixtures.TempDir())
        self.backend = flat_file.FlatFile(self.tempdir.path)

    def test_create_volume(self):
        vol = self.backend.create_volume(1024, 'test')
        self.assertEqual(vol.size, 1024)
        self.assertEqual(vol.name, 'test')
        self.assertTrue(os.path.exists(vol.path))
        self.assertEqual(os.path.getsize(vol.path), 1024)

    def test_delete_volume(self):
        vol = self.backend.create_volume(1024, 'test')
        self.assertTrue(os.path.exists(vol.path))
        self.backend.delete_volume(vol)
        self.assertFalse(os.path.exists(vol.path))

    def test_grow_volume(self):
        vol = self.backend.create_volume(1024, 'test')
        self.assertEqual(vol.size, 1024)
        self.assertEqual(os.path.getsize(vol.path), 1024)
        self.backend.grow_volume(vol, 1024)
        self.assertEqual(vol.size, 2048)
        self.assertEqual(os.path.getsize(vol.path), 2048)

    def test_clone_volume(self):
        vol = self.backend.create_volume(1024, 'test')
        clone = self.backend.clone_volume(vol, 'clone')
        self.assertEqual(clone.size, 1024)
        self.assertEqual(clone.name, 'clone')
        self.assertNotEqual(vol.volume_id, clone.volume_id)
        self.assertNotEqual(vol.path, clone.path)
        self.assertNotEqual(
            os.path.realpath(vol.path), os.path.realpath(clone.path))
        self.assertTrue(os.path.exists(clone.path))
        self.assertEqual(os.path.getsize(clone.path), 1024)

    def test_create_vol_with_data(self):
        vol = self.backend.create_volume(1024, 'test-file')
        with self.backend.open_volume(vol) as f:
            f.seek(0)
            f.write(b'test')
        with open(vol.path, 'rb') as f:
            self.assertEqual(f.read(4), b'test')

    def test_host_attach_detach(self):
        vol = self.backend.create_volume(1024, 'test')
        device = self.backend.host_attach(vol)
        print(device)
        self.addCleanup(self.backend.host_detach, vol)
        self.assertTrue(os.path.exists(device))
