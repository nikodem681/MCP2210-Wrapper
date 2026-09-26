# MCP2210-Wrapper

Python tools for lab automation around the Microchip MCP2210 USB-to-SPI bridge:

- a `ctypes` wrapper for Microchip's MCP2210 DLL (device discovery, GPIO, SPI, NVRAM settings);
- a driver for the 18 GHz switchboard PCB (MCP23S17 GPIO expanders, mechanical switches, AD5726 DACs);
- SCPI helpers for the R&S FSV40-N spectrum analyzer and an Anapico signal generator;
- Tkinter GUIs for the switchboard and for editing the MCP2210 USB strings.

**Windows only.** The wrapper loads the vendor DLL through `ctypes.WinDLL`.

## Layout

| Path | Contents |
| --- | --- |
| `instrumentation/PCBs/mcp2210_wrapper.py` | `MCP2210` class, a wrapper around `mcp2210_dll_um_x64.dll` |
| `instrumentation/PCBs/constants.py` | Enums for GPIO designations, directions, SPI settings, etc. |
| `instrumentation/PCBs/Switchboard_18GHz.py` | `Switchboard_18GHz`, `MechanicalSwitcher`, `AD5726` |
| `instrumentation/PCBs/MCP2210/` | Microchip MCP2210 DLL (x64/x86) and header |
| `instrumentation/SA/FSV40N.py` | Spectrum analyzer and signal generator SCPI helpers |
| `GUI/UI.py` | Switchboard control GUI |
| `GUI/UI_WriteRead_Description.py` | MCP2210 configurator: USB manufacturer/product strings |
| `sandbox/` | Measurement and bring-up scripts |

## Setup

Requires 64-bit Python 3.10+ (the bundled DLL is x64). Instrument control goes
through PyVISA, so a VISA library such as NI-VISA must be installed for the
spectrum analyzer and generator scripts.

```
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

The editable install makes the `instrumentation` package importable from any
script. In PyCharm it also works without installing, since run configurations
add the project root to `PYTHONPATH`.

## Usage

```python
from instrumentation.PCBs.mcp2210_wrapper import MCP2210

mcp = MCP2210()
print(mcp.get_connected_device_count())

handle = mcp.open_device_by_index(index=0)
print(mcp.get_serial_number(handle))
mcp.close_device(handle)
```

```python
from instrumentation.PCBs.Switchboard_18GHz import Switchboard_18GHz

swb = Switchboard_18GHz()
swb.connect(serial_no)
swb.reset_PCB()
```

Scripts:

| Command | What it does |
| --- | --- |
| `python GUI/UI.py` | Switchboard GUI: connect by serial number, toggle switches, set DAC outputs |
| `python GUI/UI_WriteRead_Description.py` | Reads and writes the manufacturer/product strings in NVRAM; with several MCP2210s plugged in, Connect steps to the next one |
| `python sandbox/main.py` | Lists connected MCP2210 serial numbers, connects to the first switchboard and resets it |
| `python sandbox/frequency_response.py` | Generator to analyzer frequency sweep; saves a `.mat` file to `data/` and plots it (`--help` for options) |
| `python sandbox/example.py` | Temperature sensor readout over SPI with a live plot, logged to `data/temperature_log.csv` |
| `python sandbox/Graphic.py [file.mat]` | Plots a saved sweep (default: the newest `.mat` in `data/`) |
| `python sandbox/test_mcp2210_descriptors.py` | Reads the device descriptors and round-trips the NVRAM strings (writes, then restores the originals) |

Measurement output (`data/`, `*.mat`, `temperature_log.csv`) is not tracked by git.

## Tests

The tests run without hardware. `tests/fake_dll/fake_mcp2210.c` implements the
MCP2210 DLL API and is compiled against the vendor header, so the ctypes
signatures, the constants and the switchboard SPI traffic are checked against
it. Building it needs a C compiler (gcc/clang), so on Windows run the tests in
WSL or let CI run them; the GUI tests also need Tk and a display.

```
pip install -e . pytest ruff
ruff check .
pytest
```

GitHub Actions runs the same on every push to `main` and on pull requests.

## Third-party files

`instrumentation/PCBs/MCP2210/` and `MCP2210 DLL User Guide.pdf` are from
Microchip's MCP2210 DLL package. `libusb-1.0.dll` is from the
[libusb](https://libusb.info) project.
