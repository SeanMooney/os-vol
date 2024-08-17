# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import typing as ty
import uuid

from os_vol.objects import types
from os_vol.objects import volume


@dataclasses.dataclass
class StoragePool:
    """
    StoragePool is an abstract class that represents a storage pool instance.
    """

    name: str = dataclasses.field(default='base')
    pool_type: str = dataclasses.field(default='fake')
    allocations: ty.Dict[uuid.UUID, volume.Volume] = dataclasses.field(
        default_factory=dict)
    backend: ty.Any = dataclasses.field(default=None)

    def __str__(self):
        return self.storage_summary()

    def __repr__(self):
        return self.name

    def allocate_volume(
            self, volume_name: str, size: types.SIZE_MB) -> volume.Volume:
        """
        Create a volume in the storage pool.
        """
        vol = self.backend.allocate_volume(volume_name, size)
        self.allocations[vol.volume_id] = vol
        return vol

    def deallocate_volume(self, volume: volume.Volume) -> None:
        """
        Delete a volume from the storage pool.
        """
        self.backend.deallocate_volume(volume)
        del self.allocations[volume.volume_id]

    def list_volumes(self) -> ty.List[volume.Volume]:
        """
        List all volumes in the storage pool.
        """
        return list(self.allocations.values())

    def get_capacity(self) -> types.SIZE_MB:
        """
        Get the total capacity of the storage pool.
        """
        return self.backend.get_capacity()

    def usage(self) -> types.SIZE_MB:
        """
        Get the total usage of the storage pool.
        """
        return sum([v.size for v in self.allocations.values()])

    def grow_volume(self, volume: volume.Volume, size: types.SIZE_MB) -> None:
        """
        Grow the volume by `size`.
        """
        self.backend.grow_volume(volume, size)

    def storage_summary(self) -> ty.Dict[str, ty.Any]:
        """
        Return a summary of the storage pool.
        """
        return {
            'name': self.name,
            'pool_type': self.pool_type,
            'volumes': len(self.allocations),
            'capacity': self.get_capacity(),
            'usage': self.usage(),
        }
