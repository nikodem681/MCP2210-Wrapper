import ctypes

import pytest

from conftest import spi_log
from instrumentation.PCBs import constants
from instrumentation.PCBs.Switchboard_18GHz import Switchboard_18GHz

FAKE_SERIAL = "0001234567"
CS_GPIO4 = 0b000010000


def fake_int(swb, name):
    return ctypes.c_int.in_dll(swb.mcp.dll, name).value


@pytest.fixture
def swb(fake_dll_path):
    board = Switchboard_18GHz()
    board.connect(FAKE_SERIAL)
    return board


def test_connect_configures_the_mcp2210(swb):
    cfg = swb.mcp.get_gpio_config(swb.handle, constants.cfgSelector.MCP2210_VM_CONFIG)
    assert cfg["gpio_pin_des"] == [0, 0, 0, 1, 1, 0, 0, 1, 1]
    assert cfg["dflt_gpio_output"] == 0b111011000
    assert cfg["dflt_gpio_dir"] == 0
    assert cfg["spi_bus_rel_en"] == constants.spiBusRelEn.MCP2210_SPI_BUS_RELEASE_DISABLED == 1

    spi = swb.mcp.get_spi_config(swb.handle, constants.cfgSelector.MCP2210_VM_CONFIG)
    assert spi["idleCsVal"] == 0x1FF
    assert spi["activeCsVal"] == 0
    assert spi["spiMd"] == 3


def test_connect_initializes_the_io_expanders(swb):
    log = spi_log(swb.mcp.dll)
    assert len(log) == 25
    assert all(cs == CS_GPIO4 for _, cs in log)
    assert [tx for tx, _ in log[:5]] == [
        [0x40, 0x0A, 0x80],  # IOCON.BANK = 1
        [0x40, 0x00, 0x00],  # IODIRA
        [0x40, 0x10, 0x00],  # IODIRB
        [0x40, 0x0A, 0x00],  # OLATA
        [0x40, 0x1A, 0x00],  # OLATB
    ]
    assert log[5][0][0] == 0x42


def test_mechanical_switch_toggles(swb):
    sw = swb.Mech_sw_2
    assert sw.get_state() == "NC"
    sw.toggle_state()
    assert sw.get_state() == "NO"
    assert swb.MCP23S17_get_output(5) == 0b10
    swb.Mech_sw_4.set_state("NO")
    assert swb.MCP23S17_get_output(5) == 0b1010
    sw.toggle_state()
    assert swb.MCP23S17_get_output(5) == 0b1000


def test_mcp23s17_set_output_writes_both_ports(swb):
    swb.mcp.dll.fake_reset_log()
    swb.MCP23S17_set_output(5, 0x1234)
    assert [tx for tx, _ in spi_log(swb.mcp.dll)] == [[0x4A, 0x0A, 0x34], [0x4A, 0x1A, 0x12]]
    assert swb.MCP23S17_get_output(5) == 0x1234


def test_dac_frame_and_ldac_pulse(swb):
    swb.mcp.dll.fake_reset_log()
    swb.AD5726_1.set_output_voltage(3, 0.0)  # mid-scale: code 2048
    assert spi_log(swb.mcp.dll) == [([0xC8, 0x00], CS_GPIO4)]
    _, gpio = swb.mcp.get_gpio_pin_val(swb.handle)
    assert gpio & 0b111 == 2           # MUX on the DAC's channel
    assert gpio & (1 << 6)             # LDAC back high


def test_dac_rejects_bad_arguments(swb):
    with pytest.raises(ValueError):
        swb.AD5726_1.set_output_voltage(4, 0.0)
    with pytest.raises(ValueError):
        swb.AD5726_1.set_output_voltage(0, 1.5)


def test_close_is_idempotent_and_reconnect_closes_first(swb):
    swb.connect(FAKE_SERIAL)
    assert fake_int(swb, "fake_open_handles") == 1
    swb.CloseDevice()
    swb.CloseDevice()
    assert fake_int(swb, "fake_close_calls") == 2  # one from reconnect, one from the first CloseDevice
    assert fake_int(swb, "fake_open_handles") == 0
    assert not swb.is_connected


def test_operations_need_a_connection(fake_dll_path):
    board = Switchboard_18GHz()
    with pytest.raises(RuntimeError, match="not connected"):
        board.reset_PCB()
    board.CloseDevice()  # no-op
