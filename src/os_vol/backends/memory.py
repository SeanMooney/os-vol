# -*- coding: utf-8 -*-
import copy
import dataclasses
import io
import typing as ty
import uuid

from os_vol.backends import api


@dataclasses.dataclass
class Memory(api.Backend):
    """
    Memory is a fake storage backend that stores volumes in memory.
    """

    volumes: ty.Dict[uuid.UUID, io.StringIO] = dataclasses.field(
        default_factory=dict)

    def create_volume(self, size: int,  name: str) -> 'api.volume.Volume':
        backend = self
        vol_id = uuid.uuid4()
        vol_path = f'mem://vol-{vol_id}'
        vol = api.volume.Volume(path=vol_path, name=name, volume_id=vol_id,
                                size=size, backend=backend)
        self.volumes[vol.volume_id] = io.StringIO('\0' * size)
        return vol

    def delete_volume(self, volume):
        del self.volumes[volume.volume_id]

    def grow_volume(self, volume, size):
        data = self.volumes[volume.volume_id]
        data.seek(volume.size)
        data.write('\0' * size)
        volume.size = len(data.getvalue())
        self.volumes[volume.volume_id] = data

    def clone_volume(self, volume, name):
        kwargs = {
            'name': name,
            'backend': self,
            'size': volume.size,
        }
        vol_id = uuid.uuid4()
        kwargs['volume_id'] = vol_id
        vol_path = f'mem://vol-{vol_id}'
        kwargs['path'] = vol_path
        new_vol = api.volume.Volume(**kwargs)
        self.volumes[new_vol.volume_id] = (
            copy.deepcopy(self.volumes[volume.volume_id]))
        return new_vol

    def open_volume(self, volume) -> ty.IO:
        return self.volumes[volume.volume_id]
