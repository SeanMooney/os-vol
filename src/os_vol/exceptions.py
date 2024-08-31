# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

class OSVolError(Exception):
    """Base class for all os_vol exceptions."""


class OSVolBackendError(OSVolError):
    """Base class for all backend exceptions."""


class OSVolConfigError(OSVolError):
    """Base class for all configuration exceptions."""


class OSVolVolumeError(OSVolError):
    """Base class for all volume exceptions."""


class OSVolCapacityError(OSVolBackendError):
    """Exception raised when there is not enough space for a volume."""

    def __init__(self, requested: int, available: int, name: str):
        self.requested = requested
        self.available = available
        super().__init__(f'Not enough space to create volume {name}: '
                         f'{requested} requested, {available} available')
