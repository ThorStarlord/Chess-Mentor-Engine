"""Strict structural codec for trusted, explicitly selected dataclass schemas.

No pickle, eval, payload-selected imports, or arbitrary object construction.
Wire fields must match the selected schema exactly; tuples regain their type.
"""

from __future__ import annotations

import types
from dataclasses import fields, is_dataclass
from functools import lru_cache
from typing import Any, Literal, TypeVar, Union, get_args, get_origin, get_type_hints

from .store import IntegrityError, StorageError, canonical

T = TypeVar("T")
MAX_RECORD_DEPTH = 96


@lru_cache(maxsize=None)
def _hints(schema: type) -> dict[str, Any]:
    return get_type_hints(schema)


def encode_record(value: object) -> dict[str, Any]:
    """Encode a dataclass using field data rather than its presentation JSON."""
    def encode(item: object, depth: int) -> Any:
        if depth > MAX_RECORD_DEPTH:
            raise StorageError("record exceeds codec depth limit")
        if is_dataclass(item) and not isinstance(item, type):
            return {
                field.name: encode(getattr(item, field.name), depth + 1)
                for field in fields(item)
            }
        if type(item) is tuple:
            return [encode(child, depth + 1) for child in item]
        if item is None or type(item) in (str, int, float, bool):
            return item
        raise StorageError("unsupported record field type")

    if not is_dataclass(value) or isinstance(value, type):
        raise StorageError("record must be a dataclass instance")
    payload = encode(value, 0)
    canonical(payload)
    # Validate enum membership, field types, and constructor invariants on save too.
    decode_record(payload, type(value))
    return payload


def decode_record(payload: dict[str, Any], schema: type[T]) -> T:
    """Decode only the caller's trusted schema, never a type named by stored data."""
    def decode(value: Any, expected: Any, depth: int) -> Any:
        if depth > MAX_RECORD_DEPTH:
            raise IntegrityError("record exceeds codec depth limit")
        origin, args = get_origin(expected), get_args(expected)
        if origin in (Union, types.UnionType):
            matches = []
            for candidate in args:
                try:
                    matches.append(decode(value, candidate, depth + 1))
                except (IntegrityError, TypeError, ValueError):
                    continue
            if len(matches) != 1:
                raise IntegrityError("record does not match exactly one union schema")
            return matches[0]
        if origin is Literal:
            if not any(type(value) is type(item) and value == item for item in args):
                raise IntegrityError("invalid literal value in record")
            return value
        if expected is type(None):
            if value is not None:
                raise IntegrityError("expected null")
            return None
        if expected in (str, int, float, bool):
            if type(value) is not expected:
                raise IntegrityError("record field has the wrong primitive type")
            return value
        if origin is tuple:
            if type(value) is not list:
                raise IntegrityError("tuple wire value must be an array")
            if len(args) == 2 and args[1] is Ellipsis:
                return tuple(decode(child, args[0], depth + 1) for child in value)
            if len(value) != len(args):
                raise IntegrityError("fixed tuple length mismatch")
            return tuple(
                decode(child, item_type, depth + 1)
                for child, item_type in zip(value, args)
            )
        if isinstance(expected, type) and is_dataclass(expected):
            names = {field.name for field in fields(expected)}
            if type(value) is not dict or set(value) != names:
                raise IntegrityError("record fields do not match the supported schema")
            hints = _hints(expected)
            return expected(**{
                name: decode(value[name], hints[name], depth + 1) for name in names
            })
        raise IntegrityError("unsupported record schema")

    try:
        return decode(payload, schema, 0)
    except (TypeError, ValueError, KeyError, RecursionError) as exc:
        raise IntegrityError(f"invalid stored record: {exc}") from exc
