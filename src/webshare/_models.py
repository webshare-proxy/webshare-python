"""Decoding helpers that map wire JSON onto plain dataclass models.

The decoder is tolerant by design:

* unknown/extra wire fields are ignored (forward compatibility),
* missing fields decode to ``None``,
* RFC 3339 timestamp strings are parsed into ``datetime`` where the model
  declares a ``datetime`` field,
* values that cannot be coerced to the declared type are kept as-is rather
  than raising.

Field-name aliasing: a trailing underscore in a dataclass field name is
stripped when looking up the wire key (used for reserved words such as
``from_`` -> ``from``).
"""

from __future__ import annotations

import dataclasses
import re
from datetime import datetime
from functools import cache
from types import UnionType
from typing import Any, TypeVar, Union, cast, get_args, get_origin, get_type_hints

ModelT = TypeVar("ModelT")

_ISO_RE = re.compile(
    r"^(?P<head>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})"
    r"(?:\.(?P<frac>\d+))?"
    r"(?P<tz>[+-]\d{2}:?\d{2}|[+-]\d{2})?$"
)


def _normalize_iso(text: str) -> str:
    """Normalize an RFC 3339 timestamp for Python 3.10's stricter
    ``fromisoformat`` (pad/truncate fractional seconds to 6 digits, insert
    the colon in numeric offsets)."""
    match = _ISO_RE.match(text)
    if match is None:
        return text
    head = match.group("head")
    frac = match.group("frac")
    tz = match.group("tz")
    out = head
    if frac is not None:
        out += "." + frac[:6].ljust(6, "0")
    if tz is not None:
        if len(tz) == 3:  # +HH
            tz += ":00"
        elif ":" not in tz:  # +HHMM
            tz = tz[:3] + ":" + tz[3:]
        out += tz
    return out


def parse_datetime(value: str) -> datetime:
    """Parse an RFC 3339 / ISO 8601 timestamp into a ``datetime``."""
    text = value.strip()
    # Python 3.10's fromisoformat does not accept a trailing "Z".
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        # Python 3.10 only accepts isoformat() output (3/6-digit fractions,
        # colon offsets); normalize other valid RFC 3339 spellings.
        return datetime.fromisoformat(_normalize_iso(text))


@cache
def _type_hints(cls: type) -> dict[str, Any]:
    return get_type_hints(cls)


def _coerce(tp: Any, value: Any) -> Any:
    """Best-effort coercion of ``value`` to the declared type ``tp``."""
    if value is None:
        return None
    origin = get_origin(tp)
    if origin in (Union, UnionType):
        args = [a for a in get_args(tp) if a is not type(None)]
        if len(args) == 1:
            return _coerce(args[0], value)
        return value
    if tp is Any or tp is object:
        return value
    if tp is datetime:
        if isinstance(value, str):
            try:
                return parse_datetime(value)
            except ValueError:
                return value
        return value
    if dataclasses.is_dataclass(tp) and isinstance(tp, type):
        if isinstance(value, dict):
            return decode(tp, value)
        return value
    if origin is list:
        if isinstance(value, list):
            (item_tp,) = get_args(tp) or (Any,)
            return [_coerce(item_tp, item) for item in value]
        return value
    if origin is tuple:
        member_types = get_args(tp)
        if isinstance(value, (list, tuple)) and len(member_types) == len(value):
            return tuple(_coerce(a, v) for a, v in zip(member_types, value, strict=True))
        return value
    if origin is dict:
        if isinstance(value, dict):
            dict_args = get_args(tp)
            value_tp = dict_args[1] if len(dict_args) == 2 else Any
            return {k: _coerce(value_tp, v) for k, v in value.items()}
        return value
    if tp is float and isinstance(value, int) and not isinstance(value, bool):
        return float(value)
    return value


def decode(cls: type[ModelT], data: object) -> ModelT:
    """Decode a JSON object into the dataclass ``cls``.

    Unknown wire fields are ignored and missing fields become ``None``.
    """
    if not isinstance(data, dict):
        raise TypeError(f"Cannot decode {cls.__name__} from {type(data).__name__}")
    hints = _type_hints(cast(type, cls))
    kwargs: dict[str, Any] = {}
    for field in dataclasses.fields(cast(Any, cls)):
        wire_name = field.name[:-1] if field.name.endswith("_") else field.name
        raw = data.get(wire_name)
        kwargs[field.name] = _coerce(hints.get(field.name, Any), raw)
    return cls(**kwargs)
