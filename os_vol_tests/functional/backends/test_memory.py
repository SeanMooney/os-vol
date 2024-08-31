# -*- coding: utf-8 -*-
from os_vol.backends import memory
from os_vol_tests import base_test


class TestMemoryBackend(base_test.OSVTestCase):
    def setUp(self):
        super().setUp()
        self.backend = memory.Memory()

    def test_create_volume(self):
        vol = self.backend.create_volume(1024, 'test')
        self.assertEqual(vol.size, 1024)
        self.assertIn(vol.volume_id, self.backend.volumes)
        self.assertEqual(vol.name, 'test')

    def test_delete_volume(self):
        vol = self.backend.create_volume(1024, 'test')
        self.backend.delete_volume(vol)
        self.assertNotIn(vol.volume_id, self.backend.volumes)

    def test_grow_volume(self):
        vol = self.backend.create_volume(1024, 'test')
        self.backend.grow_volume(vol, 1024)
        self.assertEqual(vol.size, 2048)
        self.assertEqual(
            len(self.backend.volumes[vol.volume_id].getvalue()),
            2048)

    def test_clone_volume(self):
        vol = self.backend.create_volume(1024, 'test')
        new_vol = self.backend.clone_volume(vol, 'clone')
        self.assertNotEqual(vol.volume_id, new_vol.volume_id)
        self.assertEqual(vol.size, new_vol.size)
        self.assertEqual(new_vol.name, 'clone')
        self.assertIn(new_vol.volume_id, self.backend.volumes)
