# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import os
import typing as ty
import uuid

from os_vol.objects import types

SIZE_MB = types.SIZE_MB


@dataclasses.dataclass
class Volume:
    """
    Volume is an abstract dataclass that represents a volume instance.
    """

    path: str
    name: ty.Optional[str] = None
    volume_id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    size: SIZE_MB = dataclasses.field(default=SIZE_MB(0))
    volume_type: str = dataclasses.field(default='base')
    pool_ref: ty.Any = dataclasses.field(default=None)
    backend: ty.Any = dataclasses.field(default=None)

    def __str__(self):
        return self.volume_summary()

    def __repr__(self):
        return self.name

    def volume_summary(self) -> str:
        """
        Return a summary of the volume.
        """
        return (f'Volume {self.name} ({self.volume_id}) of size {self.size} '
                f'in pool {self.pool_ref}')

    def delete(self) -> None:
        """
        Delete the volume.
        """
        self.pool_ref.deallocate_volume(self)

    def grow(self, size: SIZE_MB) -> 'Volume':
        """
        Grow the volume by `size`.
        """
        self.pool_ref.grow_volume(self, size)
        return self

    def clone(self, name: str) -> 'Volume':
        """
        Clone the volume with a new name.
        """
        return self.pool_ref.clone_volume(self, name)

    def open(self) -> os.PathLike:
        """
        Open the volume.
        returns: file object
        """
        return self.pool_ref.open_volume(self)
