# -*- coding: utf-8 -*-
import abc
import io

from os_vol.objects import types
from os_vol.objects import volume


class Backend(abc.ABC):
    """
    Backend is an abstract class that represents a storage backend.

    A storage backend is responsible for managing the storage for volumes
    within a storage pool.
    """
    @abc.abstractmethod
    def create_volume(self, size: int,  name: str) -> volume.Volume:
        pass

    @abc.abstractmethod
    def delete_volume(self, volume: volume.Volume):
        pass

    @abc.abstractmethod
    def grow_volume(self, volume: volume.Volume, size: types.SIZE_MB):
        pass

    @abc.abstractmethod
    def clone_volume(self, volume: volume.Volume, name: str) -> volume.Volume:
        pass

    @abc.abstractmethod
    def open_volume(self, volume: volume.Volume) -> io.TextIOWrapper:
        pass
