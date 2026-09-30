import json

import pytest

from greenheat.enums import GreenHeatButtonType, GreenHeatEventType
from greenheat.models import GreenHeatMessage


def make_payload(**overrides) -> dict:
    payload = {
        "mobile": False,
        "x": 0.25,
        "y": 0.75,
        "button": "left",
        "shift": True,
        "ctrl": False,
        "alt": False,
        "time": 1_700_000_000_000,
        "latency": 12,
        "type": "click",
        "id": "123456",
        "is_anonymous": False,
        "latency_ms": 12,
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize("encode", [lambda d: d, json.dumps, lambda d: json.dumps(d).encode()])
def test_parses_dict_str_bytes(encode):
    msg = GreenHeatMessage(encode(make_payload()))

    assert msg.button is GreenHeatButtonType.LEFT
    assert msg.type is GreenHeatEventType.CLICK
    assert msg.time.year == 2023
    assert msg.position == (0.25, 0.75)
    assert msg.to_dict() == make_payload()


def test_does_not_modify_caller_dict():
    payload = make_payload()
    GreenHeatMessage(payload)
    assert payload == make_payload()


def test_is_in_box():
    msg = GreenHeatMessage(make_payload(x=0.5, y=0.5))
    assert msg.is_in_box(0.0, 0.0, 0.5, 0.5)
    assert msg.is_in_box(0.5, 0.5, 1.0, 1.0)
    assert not msg.is_in_box(0.0, 0.0, 0.4, 0.4)


def test_is_in_circle():
    msg = GreenHeatMessage(make_payload(x=0.5, y=0.5))
    assert msg.is_in_circle(0.5, 0.6, 0.1)
    assert not msg.is_in_circle(0.5, 0.7, 0.1)


def test_screen_position_and_distance():
    msg = GreenHeatMessage(make_payload(x=0.5, y=0.25))
    assert msg.screen_position(1920, 1080) == (960, 270)
    assert msg.distance_from_position(0.5, 0.0) == pytest.approx(0.25)
