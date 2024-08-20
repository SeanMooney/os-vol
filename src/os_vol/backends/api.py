# -*- coding: utf-8 -*-
import abc
import contextlib
import typing as ty

from os_vol.objects import types
from os_vol.objects import volume


class Backend(abc.ABC):
    """
    Backend is an abstract class that represents a storage backend.

    A storage backend is responsible for managing the storage for volumes
    within a storage pool.
    """
    @abc.abstractmethod
    def create_volume(
            self, size: types.SIZE_BYTES,  name: str) -> volume.Volume:
        pass

    @abc.abstractmethod
    def delete_volume(self, volume: volume.Volume):
        pass

    @abc.abstractmethod
    def grow_volume(self, volume: volume.Volume, size: types.SIZE_BYTES):
        """Grow a volume by size in byets."""
        pass

    @abc.abstractmethod
    def clone_volume(self, volume: volume.Volume, name: str) -> volume.Volume:
        """Clone a volume with a new name"""
        pass

    def shallow_clone_volume(
            self, volume: volume.Volume, name: str) -> volume.Volume:
        """Create a shallow clone of a volume.

        A shallow clone is a clone of a volume that shares the same data as the
        original volume. This is useful for sharing backing files or
        creating a snapshot of a volume without duplicating the data.

        This method falls back to `clone_volume` if the backend does not
        support shallow clones.
        """
        return self.clone_volume(volume, name)

    @abc.abstractmethod
    def open_volume(self, volume: volume.Volume) -> ty.IO:
        """Open a volume for reading and writing in binary mode."""
        pass

    @abc.abstractmethod
    def host_attach(self, volume: volume.Volume) -> str:
        """Attach a volume as a block device to the host."""
        pass

    @abc.abstractmethod
    def host_detach(self, volume: volume.Volume) -> None:
        """Detach a volume from the host."""
        pass

    @contextlib.contextmanager
    def attach(self, volume: volume.Volume) -> ty.Generator:
        """Attach a volume to the host."""
        try:
            device = self.host_attach(volume)
            yield device
        finally:
            self.host_detach(volume)
