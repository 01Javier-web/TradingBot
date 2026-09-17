"""Pruebas del mecanismo de parada."""

import pytest

from risk.kill_switch import KillSwitch


def test_kill_switch_stops_when_triggered() -> None:
    switch = KillSwitch()
    switch.trigger("prueba de seguridad")
    with pytest.raises(RuntimeError, match="prueba de seguridad"):
        switch.check()


def test_kill_switch_can_be_reset() -> None:
    switch = KillSwitch()
    switch.trigger("temporary")
    switch.reset()
    switch.check()
    assert switch.reason is None
