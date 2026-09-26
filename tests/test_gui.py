"""Smoke tests for the Tk GUIs, driven through the fake DLL. Skipped without Tk or a display."""
import ctypes

import pytest

from conftest import spi_log

tk = pytest.importorskip("tkinter")
from tkinter import messagebox  # noqa: E402

FAKE_SERIAL = "0001234567"


class Calls(list):
    """Dialog log; `answers` queues replies for askyesno."""


@pytest.fixture
def dialogs(monkeypatch):
    """Record dialogs instead of blocking on them; askyesno answers from `answers`."""
    calls = Calls()
    answers = []
    for name in ("showinfo", "showwarning", "showerror"):
        monkeypatch.setattr(messagebox, name, lambda *a, _n=name, **k: calls.append((_n, a[0] if a else "")))

    def askyesno(*a, **k):
        calls.append(("askyesno", a[0] if a else ""))
        return answers.pop(0) if answers else True
    monkeypatch.setattr(messagebox, "askyesno", askyesno)
    calls.answers = answers
    return calls


@pytest.fixture
def make_app(fake_dll_path, dialogs):
    apps = []

    def make(cls):
        try:
            app = cls()
        except tk.TclError as e:
            pytest.skip(f"no display: {e}")
        app.withdraw()
        apps.append(app)
        return app
    yield make
    for app in apps:
        try:
            app.destroy()
        except tk.TclError:
            pass


def test_switchboard_gui(make_app, dialogs, fake_dll_path):
    from GUI.UI import SwitchboardApp
    app = make_app(SwitchboardApp)
    assert app.serial_var.get() == FAKE_SERIAL

    app.on_mech_switch(1)  # before connecting: warning, no crash
    assert dialogs[-1] == ("showwarning", "Not connected")
    app.on_slider_change(1, "0.5")  # ignored while disconnected

    app.on_connect()
    assert app.status_var.get() == f"Connected: {FAKE_SERIAL}"
    app.on_mech_switch(2)
    assert app.swb.Mech_sw_2.state == "NO"

    app.swb.mcp.dll.fake_reset_log()
    app.on_slider_change(4, "0.0")  # var_4 -> AD5726_2 channel 0
    assert spi_log(app.swb.mcp.dll) == [([0x08, 0x00], 0b10000)]

    app.on_disconnect()
    assert app.status_var.get() == "Not connected"
    app.on_close()


def test_switchboard_gui_without_devices(make_app, dialogs, fake_dll_path):
    ctypes.c_int.in_dll(ctypes.CDLL(fake_dll_path), "fake_device_count").value = 0
    from GUI.UI import SwitchboardApp
    app = make_app(SwitchboardApp)
    assert dialogs[-1] == ("showwarning", "No device")
    app.on_connect()
    assert app.status_var.get() == "Not connected"


def test_switchboard_gui_reports_errors(make_app, dialogs):
    from GUI.UI import SwitchboardApp
    app = make_app(SwitchboardApp)
    app.serial_var.set("wrong serial")
    app._safe(app.on_connect)()
    assert dialogs[-1] == ("showerror", "Error")
    assert not app.swb.is_connected


def test_configurator_gui(make_app, dialogs):
    from GUI.UI_WriteRead_Description import Mcp2210App
    app = make_app(Mcp2210App)

    app.on_open_device()
    assert app.status_var.get() == f"Connected: SN {FAKE_SERIAL} (1 of 1)"
    assert app.prod_read_var.get() == "MCP2210 USB to SPI Master"

    app.on_open_device()
    assert dialogs[-1] == ("showinfo", "Already connected")

    dialogs.answers.append(False)
    app.prod_write_var.set("BB Controller, 1234, 1.0")
    app.on_write_product()
    assert app.prod_read_var.get() == "MCP2210 USB to SPI Master"  # declined, nothing written

    app.on_write_product()
    assert dialogs[-1] == ("askyesno", "Write to NVRAM")
    assert app.prod_read_var.get() == "BB Controller, 1234, 1.0"

    app.mfg_write_var.set("x" * 30)
    app.on_write_manufacturer()
    assert dialogs[-1] == ("showwarning", "Too long")

    app.on_close()
