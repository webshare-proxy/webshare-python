"""Unit tests for the wire decode helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from webshare._models import parse_datetime


def test_parse_datetime_standard() -> None:
    parsed = parse_datetime("2019-06-09T23:34:00.095501-07:00")
    assert parsed == datetime(2019, 6, 9, 23, 34, 0, 95501, tzinfo=timezone(timedelta(hours=-7)))


def test_parse_datetime_zulu() -> None:
    parsed = parse_datetime("2022-06-14T11:58:10Z")
    assert parsed == datetime(2022, 6, 14, 11, 58, 10, tzinfo=timezone.utc)


def test_parse_datetime_odd_fraction_lengths() -> None:
    # Two-digit fraction: rejected by Python 3.10's fromisoformat unless
    # normalized.
    parsed = parse_datetime("2022-06-14T11:58:10.24-07:00")
    assert parsed.microsecond == 240000
    # Seven-digit fraction is truncated to microseconds.
    parsed = parse_datetime("2022-06-14T11:58:10.1234567+00:00")
    assert parsed.microsecond == 123456


def test_parse_datetime_offset_without_colon() -> None:
    parsed = parse_datetime("2022-06-14T11:58:10.5+0130")
    assert parsed.microsecond == 500000
    assert parsed.utcoffset() == timedelta(hours=1, minutes=30)
