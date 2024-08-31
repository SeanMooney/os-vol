# -*- coding: utf-8 -*-
import dataclasses
import json
import subprocess  # nosec B404
import typing as ty
import uuid

from oslo_utils import units

from os_vol.backends import api
from os_vol import exceptions
from os_vol import file_dict
from os_vol.objects import types
from os_vol.objects import volume


@dataclasses.dataclass
class VGS():
    name: str
    size: int


@dataclasses.dataclass
class LVMFatPool(api.Backend):
    """
    LVMFatPool is a storage backend that uses an LVM Volume Group
    to store volumes.

    This backend requires the `lvm2` package to be installed.
    """

    SHELVE_FILE = 'volumes.shelve'
    LVM_DOMAIN = uuid.UUID('d7ca5862-47b2-4ff9-927e-2bb04af727b8')

    state_dir: str
    vg_name: str
    volumes: file_dict.TypedFileDict
    capacity: types.SIZE_MB = 0

    def __init__(self, state_dir: str,  vg_name: str):
        self.state_dir = state_dir
        self.vg_name = vg_name
        self.volumes = file_dict.TypedFileDict(
            f'{self.state_dir}/{self.vg_name}', volume.VolumeSummary)
        info = self._ensure_vg_exists()
        self.capacity: types.SIZE_MB = info.size // units.Mi

    def get_vg_info(self) -> VGS:
        try:
            vg_info_raw = subprocess.run(
                ['/usr/bin/env', 'sudo', 'vgs', '--report-format', 'json',
                 '--units', 'B', self.vg_name],
                capture_output=True, check=True)  # nosec B603
            vg_info = json.loads(vg_info_raw.stdout)
            if 'report' not in vg_info or 'vg' not in vg_info['report'][0]:
                raise exceptions.OSVolBackendError(
                    f'Failed to get VG info for {self.vg_name}'
                )
            report = vg_info['report'][0]
            vg = report['vg'][0]
            return VGS(name=vg['vg_name'], size=int(vg['vg_size'][:-2]))
        except subprocess.CalledProcessError as e:
            raise exceptions.OSVolBackendError(
                f'Failed to get VG info for {self.vg_name}: {e}'
            )

    def _ensure_vg_exists(self) -> VGS:
        try:
            vg_info = self.get_vg_info()
            if self.vg_name != vg_info.name:
                raise exceptions.OSVolConfigError(
                    f'Volume Group {self.vg_name} does not exist'
                )
        except exceptions.OSVolBackendError as e:
            raise exceptions.OSVolConfigError(
                f'Failed to check for Volume Group {self.vg_name}: {e}'
            )
        return vg_info

    @property
    def used_space(self) -> types.SIZE_MB:
        size = 0
        vols = self.volumes.values()
        for vol in vols:
            size += vol.size
        return size // units.Mi

    @property
    def free_space(self) -> types.SIZE_MB:
        return self.capacity - self.used_space

    def create_volume(
            self, size: types.SIZE_BYTES, name: str) -> 'api.volume.Volume':

        if size > self.free_space * units.Mi:
            raise exceptions.OSVolCapacityError(
                requested=size, available=self.free_space, name=name
            )
        vol_id = uuid.uuid5(self.LVM_DOMAIN, name)
        lvcreate_cmd = [
            'sudo', 'lvcreate', '-L', f'{size // units.Mi}M', '-n', str(
                vol_id),
            self.vg_name
        ]
        try:
            subprocess.run(lvcreate_cmd, check=True)  # nosec B603
        except subprocess.CalledProcessError as e:
            raise exceptions.OSVolBackendError(
                f'Failed to create LV {vol_id}: {e}'
            )
        vol = api.volume.Volume(
            name=name, volume_id=vol_id, size=size, backend=self,
            path='')
        self.volumes[str(vol.volume_id)] = vol.volume_summary()
        return vol

    def delete_volume(self, volume):
        lvremove_cmd = [
            'sudo', 'lvremove', '-f',
            f'{self.vg_name}/{str(volume.volume_id)}']
        try:
            subprocess.run(lvremove_cmd, check=True)  # nosec B603
        except subprocess.CalledProcessError as e:
            raise exceptions.OSVolBackendError(
                f'Failed to delete LV {volume.volume_id}: {e}'
            )
        del self.volumes[str(volume.volume_id)]

    def grow_volume(self, volume, size):
        raise NotImplementedError()

    def clone_volume(self, volume, name):
        raise NotImplementedError()

    def open_volume(self, volume) -> ty.IO:
        raise NotImplementedError()

    def host_attach(self, volume) -> str:
        """Attach a volume as a block device to the host.

        The flat file backend uses a loopback device to attach the backing file
        to the host.
        """

        raise NotImplementedError()

    def host_detach(self, volume) -> None:
        """Detach a volume from the host.

        The flat file backend uses a loopback device
        """
        raise NotImplementedError()
        self.volumes[str(volume.volume_id)] = volume.volume_summary()
