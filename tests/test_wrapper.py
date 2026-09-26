import ctypes
import re

import pytest

from conftest import HEADER, spi_log
from instrumentation.PCBs.mcp2210_wrapper import MCP2210

FAKE_SERIAL = "0001234567"


def header_prototypes():
    """Map Mcp2210_* function names to their parameter count, parsed from the vendor header."""
    with open(HEADER, encoding="latin-1") as f:
        text = f.read()
    protos = {}
    for name, params in re.findall(r"__stdcall\s+(Mcp2210_\w+)\s*\(([^)]*)\)", text):
        params = params.strip()
        protos[name] = 0 if params in ("", "void") else params.count(",") + 1
    return protos


def test_every_bound_function_matches_the_header(mcp):
    protos = header_prototypes()
    bound = [name for name in protos if getattr(getattr(mcp.dll, name, None), "argtypes", None) is not None]
    assert "Mcp2210_OpenBySN" in bound
    for name in bound:
        assert len(getattr(mcp.dll, name).argtypes) == protos[name], name


def test_library_version(mcp):
    assert mcp.get_library_version() == "fake-1.0"


def test_open_by_index_keeps_the_full_64_bit_handle(mcp):
    assert mcp.get_connected_device_count() == 1
    handle = mcp.open_device_by_index(index=0)
    assert handle > 0xFFFFFFFF
    assert mcp.get_serial_number(handle) == FAKE_SERIAL
    mcp.close_device(handle)


def test_open_by_serial_number(mcp):
    handle = mcp.open_device_by_sn(FAKE_SERIAL)
    assert mcp.get_serial_number(handle) == FAKE_SERIAL


def test_open_errors_are_described(mcp):
    with pytest.raises(RuntimeError, match="E_ERR_NO_SUCH_SERIALNR"):
        mcp.open_device_by_sn("nope")
    with pytest.raises(RuntimeError, match="E_ERR_NO_SUCH_INDEX"):
        mcp.open_device_by_index(index=5)


def test_string_descriptors_round_trip(mcp):
    handle = mcp.open_device_by_index()
    mcp.set_manufacturer_string(handle, "Maury Microwave")
    mcp.set_product_string(handle, "BB Controller, 1234, 1.0")
    assert mcp.get_manufacturer_string(handle) == "Maury Microwave"
    assert mcp.get_product_string(handle) == "BB Controller, 1234, 1.0"
    with pytest.raises(ValueError):
        mcp.set_product_string(handle, "x" * 30)


def test_usb_key_params(mcp):
    handle = mcp.open_device_by_index()
    params = mcp.get_usb_key_params(handle)
    assert (params["vid"], params["pid"]) == (0x04D8, 0x00DE)


def test_gpio_config_and_values(mcp):
    handle = mcp.open_device_by_index()
    outputs = {f"GPIO{i}": i % 2 for i in range(9)}
    directions = {f"GPIO{i}": 0 for i in range(9)}
    assert mcp.Set_Gpio_Config(handle, 0, [1] * 9, outputs, directions, 0, 0, 1) == 0
    cfg = mcp.get_gpio_config(handle, 0)
    assert cfg["gpio_pin_des"] == [1] * 9
    assert cfg["dflt_gpio_output"] == 0b010101010
    assert cfg["spi_bus_rel_en"] == 1

    mcp.set_gpio_pin_val(handle, 0b101)
    assert mcp.get_gpio_pin_val(handle) == (0, 0b101)
    mcp.set_gpio_pin_dir(handle, 0b1)
    assert mcp.get_gpio_pin_dir(handle) == [1, 0, 0, 0, 0, 0, 0, 0, 0]


def test_set_gpio_config_raises_on_dll_error(mcp):
    handle = mcp.open_device_by_index()
    with pytest.raises(RuntimeError, match="E_ERR_INVALID_PARAMETER"):
        mcp.Set_Gpio_Config(handle, 0, [0] * 9, 0, 0, 0, 7, 0)
    with pytest.raises(ValueError):
        mcp.Set_Gpio_Config(handle, 0, [0] * 8, 0, 0, 0, 0, 0)


def test_spi_config_round_trip(mcp):
    handle = mcp.open_device_by_index()
    mcp.set_spi_config(handle, 0, 1000000, 0x1FF, 0, 1, 1, 1, 2, 3)
    assert mcp.get_spi_config(handle, 0) == {
        "baudRate": 1000000, "idleCsVal": 0x1FF, "activeCsVal": 0, "csToDataDly": 1,
        "dataToCsDly": 1, "dataToDataDly": 1, "txferSize": 2, "spiMd": 3,
    }


def test_xfer_spi_data(mcp):
    handle = mcp.open_device_by_index()
    result = mcp.xfer_spi_data(handle, [0x40, 0x0A, 0x55], 1000000, 3, 0b10000)
    assert result["transfer_size"] == 3
    assert spi_log(mcp.dll) == [([0x40, 0x0A, 0x55], 0b10000)]
    with pytest.raises(ValueError):
        mcp.xfer_spi_data(handle, [1, 2, 3], 1000000, 2, 0b10000)


def test_xfer_spi_data_ex(mcp):
    handle = mcp.open_device_by_index()
    ret, rx = mcp.mcp2210_xfer_spi_data_ex(handle, [0xAA, 0xBB], csmask=0b100)
    assert ret == 0 and len(rx) == 2
    assert spi_log(mcp.dll) == [([0xAA, 0xBB], 0b100)]


def test_reset_error_is_described(mcp):
    handle = mcp.open_device_by_index()
    ctypes.c_int.in_dll(mcp.dll, "fake_reset_result").value = -110
    with pytest.raises(RuntimeError, match="E_ERR_HID_RW_TIMEOUT"):
        mcp.reset_device(handle)
    with pytest.raises(ValueError):
        mcp.reset_device(None)


def test_dictionary_to_binary_number():
    assert MCP2210.dictionary_to_binary_number({"GPIO0": 1, "GPIO4": 1, "GPIO8": 1}) == 0b100010001
    with pytest.raises(ValueError):
        MCP2210.dictionary_to_binary_number({"GPIO0": 2})


@pytest.mark.parametrize("raw, celsius", [
    ([0x0C, 0x87], 25.0),     # +25 °C, low status bits set
    ([0x00, 0x00], 0.0),
    ([0xF3, 0x80], -25.0),
])
def test_decode_temperature(raw, celsius):
    assert MCP2210.decode_temperature({"data_rx": raw}) == celsius


def test_describe_unknown_error():
    assert "Unknown error" in MCP2210.describe_mcp2210_error(-9999)
