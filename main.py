from mcp2210_wrapper import MCP2210
import constants

# Путь к DLL
dll_path = "MCP2210/mcp2210_dll_um_x64.dll"
#
Connetced_MCP2210_devices = []
# Создаём экземпляр класса
mcp = MCP2210(dll_path)

try:
    handle = mcp.open_device_by_index(0x4D8, 0xDE, 0)

    cfg_selector = constants.cfgSelector.MCP2210_NVRAM_CONFIG  # Селектор конфигурации
    gpio_config = mcp.get_gpio_config(handle, cfg_selector)
    # GPIO Pin Designation array
    gpio_pins = [
        constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # Pin 1
        constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # Pin 2
        constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # Pin 3
        constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # Pin 4
        constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # Pin 5
        constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # Pin 6
        constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # Pin 7
        constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # Pin 8
        constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # Pin 9
    ]

    # Default GPIO output values (example: all high)
    default_output = 0xFF

    # Default GPIO direction (example: all outputs)
    default_direction = 0x00

    # Remote wakeup enabled
    remote_wakeup = constants.rmtWkupEn.MCP2210_REMOTE_WAKEUP_DISABLED

    # Interrupt mode set to detect high pulses
    interrupt_mode = constants.intPinMd.MCP2210_INT_MD_CNT_NONE
    # SPI bus release disabled
    spi_bus_release = constants.spiBusRelEn.MCP2210_SPI_BUS_RELEASE_DISABLED

    # Set the GPIO configuration
    result = mcp.Set_Gpio_Config(
        handle,
        0,  # Volatile Memory
        gpio_pins,
        default_output,
        default_direction,
        remote_wakeup,
        interrupt_mode,
        spi_bus_release
    )

    gpio_config = mcp.get_gpio_config(handle, cfg_selector)

    result = mcp.get_gpio_pin_val(handle)

    mcp.toggle_gpio(handle)
    mcp.close_device(handle)

except Exception as e:
    print(f"Ошибка: {e}")