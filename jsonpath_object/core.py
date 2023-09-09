from __future__ import annotations

from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Union,
    overload,
)


class BaseJsonPath:
    """
    A class representing a mapping for JSON-like data with support for dot-separated keys.
    """

    def __init__(
        self,
        data: Union[None, Mapping, Sequence, BaseJsonPath] = None,
        *,
        raise_on_missing: bool = True,
        default_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        """
        Initialize the _JsonPathMapping instance.

        :param data: The initial data for the mapping.
        :param raise_on_missing: Whether to raise an exception when an item is not found.
        :param default_factory: A callable used to create default values for missing items.
        """
        if data and isinstance(data, BaseJsonPath):
            self.default_factory: Optional[Callable[[], Any]] = data.default_factory
            self.raise_on_missing: bool = data.raise_on_missing
        else:
            self.default_factory = default_factory
            self.raise_on_missing = raise_on_missing
        if data is None:
            data = {}
        self.data = data

    def __contains__(self, item: Any) -> bool:
        return item in self.data

    def __str__(self) -> str:
        return str(self.to_object())

    def __repr__(self) -> str:
        return repr(self.to_object())

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Any:
        return iter(self.data)

    def __getattr__(self, item: str) -> Any:
        return getattr(self.data, item)

    @overload
    def __getitem__(self, item: int) -> Any:
        pass

    @overload
    def __getitem__(self, item: str) -> Any:
        pass

    @overload
    def __getitem__(self, item: Sequence[str]) -> Any:
        pass

    def __getitem__(self, key) -> Any:
        """
        Get an item from the mapping by key or JSON path.

        :param key: The key or JSON path to the item.
        :return: The item.
        """
        keys = self._get_keys(key)
        current_dict = self.data

        for i, k in enumerate(keys):
            if k.isdigit() and isinstance(current_dict, (list, _JsonPathList)):
                index = int(k)
                if 0 <= index < len(current_dict):
                    current_dict = current_dict[index]
                else:
                    if self.default_factory:
                        if keys[-1] == k:
                            current_dict.append(self.default_factory())
                            return current_dict[int(k)]
                        if keys[i + 1].isdigit():
                            current_dict.append([])
                        else:
                            current_dict.append({})
                        current_dict = current_dict[int(k)]
                    elif self.raise_on_missing:
                        raise IndexError(f"Index {index} out of range for list.")

            elif k in current_dict:
                current_dict = current_dict[k]  # type: ignore[call-overload]
            else:
                if self.default_factory:
                    if keys[-1] == k:
                        current_dict[k] = self.default_factory()  # type: ignore[index]
                        return current_dict[k]  # type: ignore[call-overload]
                    if keys[i + 1].isdigit():
                        current_dict[k] = _JsonPathList([])  # type: ignore[index]
                    else:
                        current_dict[k] = _JsonPathDict({})  # type: ignore[index]
                    current_dict = current_dict[k]  # type: ignore[call-overload]
                elif self.raise_on_missing:
                    raise KeyError(key)

        if isinstance(current_dict, dict):
            return _JsonPathDict(current_dict)
        elif isinstance(current_dict, list):
            return _JsonPathList(current_dict)
        else:
            return current_dict

    def __setitem__(self, key: Union[int, str, Sequence[str]], value: Any) -> None:
        """
        Set an item in the mapping by key or JSON path.

        :param key: The key or JSON path to the item.
        :param value: The value to set.
        """
        current_dict, last_key = self._find(key)
        current_dict[last_key] = value

    def __delitem__(self, key: Union[int, str, Sequence[str]]) -> None:
        """
        Delete an item from the mapping by key or JSON path.

        :param key: The key or JSON path to the item.
        """
        current_dict, last_key = self._find(key)
        del current_dict[last_key]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BaseJsonPath):
            return self.data == other.data
        elif isinstance(other, (dict, list)):
            return self.data == other
        else:
            return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def _find(self, key: Union[int, str, Iterable]) -> tuple:
        keys = self._get_keys(key)
        current_dict = self.data
        for k in keys[:-1]:
            if k.isdigit() and isinstance(current_dict, list):
                index = int(k)
                if 0 <= index < len(current_dict):
                    current_dict = current_dict[index]
                else:
                    if self.raise_on_missing:
                        raise IndexError(f"Index {index} out of range for list.")
            elif isinstance(current_dict, MutableMapping):
                if k in current_dict:
                    current_dict = current_dict[k]
                else:
                    current_dict[k] = {}
                    current_dict = current_dict[k]
        last_key: Union[str, int] = keys[-1]
        if isinstance(current_dict, list):
            last_key = int(last_key)
        return current_dict, last_key

    @staticmethod
    def _get_keys(key: Union[int, str, Iterable]) -> list[str]:
        if isinstance(key, int):
            keys = [str(key)]
        elif isinstance(key, str):
            keys = key.split(".")
        elif isinstance(key, Sequence):
            keys = list(key)
        else:
            raise NotImplementedError()

        return keys

    def to_object(self) -> Any:
        """
        Recursively converts _JsonPathDict and _JsonPathList instances to dict and list.

        :return: The converted object.
        """

        def convert(obj):
            if isinstance(obj, Mapping):
                return {key: convert(value) for key, value in obj.items()}
            elif isinstance(obj, (Sequence, Iterable)) and not isinstance(obj, str):
                return [convert(item) for item in obj]
            else:
                return obj

        return convert(self.data)


class _JsonPathDict(BaseJsonPath, Mapping):
    pass


class _JsonPathList(BaseJsonPath, Sequence):
    def __getitem__(self, item):
        return super().__getitem__(item)


class JsonPathObject(BaseJsonPath):
    def __getitem__(self, key: Union[int, str, Sequence[str]]) -> Any:
        value = super().__getitem__(key)
        if isinstance(value, Mapping):
            return JsonPathObject(value)
        elif isinstance(value, Sequence) and not isinstance(value, str):
            return JsonPathObject(value)
        else:
            return value
