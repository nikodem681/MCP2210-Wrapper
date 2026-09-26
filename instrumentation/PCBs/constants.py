"""Constants from mcp2210_dll_um.h. Values must match the vendor header (see tests/test_constants.py)."""
from enum import IntEnum


class cfgSelector(IntEnum):
    MCP2210_VM_CONFIG = 0x00  # current settings (volatile memory)
    MCP2210_NVRAM_CONFIG = 0x01  # power-up settings (NVRAM)


class pGpioPinDes(IntEnum):
    MCP2210_PIN_DES_GPIO = 0x00
    MCP2210_PIN_DES_CS = 0x01
    MCP2210_PIN_DES_FN = 0x02


class dfltGpioOutput(IntEnum):
    MCP2210_HIGH = 1
    MCP2210_LOW = 0


class dfltGpioDir(IntEnum):
    MCP2210_INPUT = 1
    MCP2210_OUTPUT = 0
    MCP2210_OUPTUT = 0  # misspelled alias of MCP2210_OUTPUT, kept for older scripts


class rmtWkupEn(IntEnum):
    MCP2210_REMOTE_WAKEUP_ENABLED = 0x01
    MCP2210_REMOTE_WAKEUP_DISABLED = 0x00


class intPinMd(IntEnum):
    MCP2210_INT_MD_CNT_HIGH_PULSES = 0x04
    MCP2210_INT_MD_CNT_LOW_PULSES = 0x03
    MCP2210_INT_MD_CNT_RISING_EDGES = 0x02
    MCP2210_INT_MD_CNT_FALLING_EDGES = 0x01
    MCP2210_INT_MD_CNT_NONE = 0x00


class spiBusRelEn(IntEnum):
    MCP2210_SPI_BUS_RELEASE_ENABLED = 0x00
    MCP2210_SPI_BUS_RELEASE_DISABLED = 0x01
