# -*- coding: utf-8 -*-
import dataclasses
import os
import shelve
import shutil
import typing as ty
import uuid

from os_vol.backends import api
from os_vol.objects import types


@dataclasses.dataclass
class FlatFile(api.Backend):
    """
    FlatFile Stores data in flat files on disk.
    """
    SHELVE_FILE = 'volumes.shelve'
    FLAT_FILE_DOMAIN = uuid.UUID('5D9B6527-52FF-4F7A-9674-8ADA17026129')

    def __init__(self, path: str):
        self.path = path
        self.volumes = shelve.open(f'{self.path}/{self.SHELVE_FILE}')
        total, _, _ = shutil.disk_usage(self.path)
        self.capasity: types.SIZE_MB = total

    @property
    def used_space(self) -> types.SIZE_MB:
        return sum([len(vol) for vol in self.volumes.values()])

    @property
    def free_space(self) -> types.SIZE_MB:
        return self.capasity - self.used_space

    def create_volume(
            self, size: types.SIZE_MB, name: str) -> 'api.volume.Volume':
        vol_id = uuid.uuid5(self.FLAT_FILE_DOMAIN, name)
        vol_path = f'{self.path}/vol-{vol_id}'
        with open(vol_path, 'w+b') as f:
            f.truncate(size)
        vol = api.volume.Volume(path=vol_path, name=name, volume_id=vol_id,
                                size=size, backend=self)
        self.volumes[str(vol.volume_id)] = vol.volume_summary()
        return vol

    def delete_volume(self, volume):
        os.remove(volume.path)
        del self.volumes[str(volume.volume_id)]

    def grow_volume(self, volume, size):
        with open(volume.path, 'r+b') as f:
            f.truncate(volume.size + size)
        volume.size += size
        self.volumes[str(volume.volume_id)] = volume.volume_summary()

    def clone_volume(self, volume, name):
        vol_id = uuid.uuid5(self.FLAT_FILE_DOMAIN, name)
        vol_path = f'{self.path}/vol-{vol_id}'
        shutil.copy(volume.path, vol_path)
        new_vol = api.volume.Volume(path=vol_path, name=name, volume_id=vol_id,
                                    size=volume.size, backend=self)
        self.volumes[str(new_vol.volume_id)] = new_vol.volume_summary()
        return new_vol

    def open_volume(self, volume) -> ty.IO:
        return open(volume.path, 'r+b')
