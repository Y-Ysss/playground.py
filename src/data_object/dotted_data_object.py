import json
import re
from copy import deepcopy
from pathlib import Path
from typing import (Any, Dict, Generator, ItemsView, Iterator, KeysView,
                    Mapping, TextIO, Tuple, Union, ValuesView, cast)


class DataObjectException(Exception):
    def __init__(self, arg=''):
        self.arg = arg


class AttributeDataObject(dict):
    def __getattr__(self, key: Any) -> Any:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key: Any, value: Any) -> None:
        self[key] = value


class DottedDataObject:
    def __init__(self, data: Mapping[str, Any] = {}, *,
                 lowercase: bool = False,
                 separator_escape: str = r'(?<!\\)\.'
                 ) -> None:
        self.lowercase = lowercase
        self.separator_escape = separator_escape
        self._config: Dict[str, Any] = self._flatten(data)

    # Property

    @property
    def lowercase(self):
        return self.__lowercase

    @lowercase.setter
    def lowercase(self, lowercase: bool):
        if not isinstance(lowercase, bool):
            raise TypeError('lowercase invalid type')
        self.__lowercase = lowercase

    @property
    def separator_escape(self):
        return self.__separator_escape.pattern

    @separator_escape.setter
    def separator_escape(self, separator_escape: str):
        self.__separator_escape = re.compile(separator_escape)

    # Public Class Methods

    @classmethod     
    def data_from_json(cls, data: Union[Path, str, TextIO], *, from_file: bool = False, lowercase: bool = False) -> 'DottedDataObject':
        if from_file:
            if isinstance(data, (Path, str)):
                data = data if isinstance(data, Path) else Path(data)
                with data.open('r') as f:
                    result = json.load(f)
            else:
                result = json.load(data)
        else:
            result = json.loads(cast(str, data))
        return cls(result, lowercase=lowercase)

    # Public Instance Methods
    # Like the built-in dict type.

    def get(self, key: str, default: Any = None) -> Union[dict, Any]:
        return self.as_dict().get(key, default)

    def update(self, data: Mapping[str, Any]) -> None:
        self._config.update(self._flatten(data))

    def setdefault(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return self[key]

    def copy(self) -> 'DottedDataObject':
        return DottedDataObject(self._config)

    def pop(self, key: str, value: Any = None) -> Any:
        try:
            value = self[key]
            del self[key]
        except KeyError:
            if value is None:
                raise
        return value

    def keys(self) -> Union['DottedDataObject', Any, KeysView[str]]:
        try:
            return self['keys']
        except KeyError:
            return cast(KeysView[str], list({'.'.join(re.split(self.separator_escape, k)[:1]) for k in set(self.as_dict().keys())}))

    def values(self) -> Union['DottedDataObject', Any, ValuesView[Any]]:
        try:
            return self['values']
        except KeyError:
            return dict(self.items()).values()

    def items(self) -> Union['DottedDataObject', Any, ItemsView[str, Any]]:
        try:
            return self['items']
        except KeyError:
            keys = cast(KeysView[str], self.keys())
            return {k: self._get_children(k) for k in keys}.items()

    def as_dict(self) -> dict:
        return self._config

    def as_attrdict(self) -> AttributeDataObject:
        return AttributeDataObject({k: DottedDataObject(v).as_attrdict() if isinstance(v, dict) else v for k, v in self.items()})

    # Internal Instance Methods

    def _iter_dict_item(self, data: Mapping[str, Any]) -> Generator[tuple[str, str, Any], None, None]:
        d = {k for k, v in data.items() if isinstance(v, (dict, DottedDataObject))}
        for name in d:
            for k, v in self._flatten(data[name]).items():
                yield name, k, v

    def _flatten(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        if self.lowercase:
            result = {name.lower() + '.' + k: v for name, k, v in self._iter_dict_item(data)}
            result.update((k.lower(), v) for k, v in data.items() if not isinstance(v, (dict, DottedDataObject)))
        else:
            result = {name + '.' + k: v for name, k, v in self._iter_dict_item(data)}
            result.update((k, v) for k, v in data.items() if not isinstance(v, (dict, DottedDataObject)))
        return result

    def _iter_item(self, data: Mapping[str, Any], key: str) -> Generator[tuple[str, Any], None, None]:
        for k, v in data.items():
            if k.startswith(key + '.'):
                yield k, v

    def _get_items(self, data: Dict[str, Any], key: str) -> Dict[str, Any]:
        if self.lowercase:
            return {k[(len(key) + 1):].lower(): v for k, v in data.items() for k, v in self._iter_item(data, key)}
        else:
            return {k[(len(key) + 1):]: v for k, v in self._iter_item(data, key)}

    def _get_children(self, key: str) -> Union[Dict[str, Any], Any]:
        data = {k[(len(key) + 1):]: v for k, v in self._iter_item(self._config, key)}
        if not data:
            attributes = re.split(self.separator_escape, key)
            if len(attributes) == 1:
                return deepcopy(self._config.get(key, {}))
            data = self._config
            while attributes:
                p = attributes[0]
                d = self._get_items(data, p)
                if d == {}:
                    return deepcopy(data.get(p, {}) if len(attributes) == 1 else {})
                data = d
                attributes = attributes[1:]
        return deepcopy(data)

    # Magic Methods
    # Like the built-in dict type.

    def __len__(self) -> int:
        return len(self.keys())

    def __getitem__(self, item: str) -> Union['DottedDataObject', Any]:
        v = self._get_children(item)
        if v == {}:
            raise KeyError(f'"{item}" key not found')
        if isinstance(v, dict):
            return DottedDataObject(v)
        else:
            return v

    def __setitem__(self, key: str, value: Any) -> None:
        self.update({key: value})

    def __delitem__(self, key: str) -> None:
        remove = []
        for k in self._config:
            kl = k.lower() if self.lowercase else k
            if kl == key or kl.startswith(key + '.'):
                remove.append(k)
        if not remove:
            raise KeyError(f'"{key}" key not found')
        for k in remove:
            del self._config[k]

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        return iter(self.items())

    def __reversed__(self) -> Iterator[Tuple[str, Any]]:
        return iter(reversed(self.items()))

    def __contains__(self, key: str) -> bool:
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __eq__(self, other) -> bool:
        return self.as_dict() == DottedDataObject(other).as_dict()

    def __repr__(self) -> str:
        return f'<DataObject: {hex(id(self))}>'

    def __str__(self) -> str:
        return str({k: v for k, v in sorted(self.as_dict().items())})



if __name__ == '__main__':
    data = DottedDataObject()
    data.update({'name': 'Alice', 'books': {'book2': {'year': 2006, 'page': 650, 'title': 'Python Developers'}, 'book1': {'year': 2005, 'page': 399, 'title': 'Python Beginners'}}, 'data': {
                'dd': {'key': 'k456', 'format': {'true': 't2', 'false': 'f2'}}, 'bb': {'key': 'k123', 'format': {'true': 'tt'}, 'version': {'1\\.3': 'Version1.3'}}, 'cc': 'fa', 'aa': 'uiss'}})
    print(data.as_dict())
    print('=====')
    attrdict = data.as_attrdict()
    print(type(data))
    print(attrdict)
    print(data.keys())
    print(len(data))
    print('name' in data)
    print(attrdict.books)

    # print(data.separator_escape)
    # print(data.lowercase)
