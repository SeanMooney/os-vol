# -*- coding: utf-8 -*-
from collections.abc import MutableMapping
import dataclasses
import os

from oslo_serialization import jsonutils as json


class FileDict(MutableMapping):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def _get_file_path(self, key):
        return os.path.join(self.base_dir, f'{key}.json')

    def __getitem__(self, key):
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            raise KeyError(key)
        with open(file_path, 'rb') as f:
            return json.load(f)

    def __setitem__(self, key, value):
        file_path = self._get_file_path(key)
        with open(file_path, 'w') as f:
            json.dump(value, f)

    def __delitem__(self, key):
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            raise KeyError(key)
        os.remove(file_path)

    def __iter__(self):
        for filename in os.listdir(self.base_dir):
            if filename.endswith('.json'):
                yield filename[:-5]

    def __len__(self):
        return len(
            [filename for filename in os.listdir(self.base_dir)
             if filename.endswith('.json')])


class TypedFileDict(FileDict):
    def __init__(self, base_dir, type_):
        super().__init__(base_dir)
        self.type_ = type_

    def __getitem__(self, key):
        value = super().__getitem__(key)
        return self.type_(**value)

    def __setitem__(self, key, value):
        if not isinstance(value, self.type_):
            raise TypeError(f'Value must be of type {self.type_}')
        if dataclasses.is_dataclass(self.type_):
            super().__setitem__(key, dataclasses.asdict(value))
        else:
            super().__setitem__(key, value)

    def __delitem__(self, key):
        super().__delitem__(key)
