"""
Bring-up script for the MCP2210 test board.

1. Configures all GPIOs as chip selects, outputs, idle high.
2. Prints the NVRAM SPI settings.
3. Writes to an MCP23008 IO expander on the GPIO4 chip select.
4. Reads a temperature sensor on the GPIO7 chip select once a minute,
   logs it to data/temperature_log.csv and plots it live.

Stop with Ctrl+C or by closing the plot window.
"""
import os
import threading
import time
from collections import deque

import matplotlib.pyplot as plt

from instrumentation.PCBs import constants
from instrumentation.PCBs.mcp2210_wrapper import MCP2210

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_PATH = os.path.join(REPO_ROOT, "data", "temperature_log.csv")

BAUD_RATE = 1000000               # SPI clock, 1 MHz
CS_MCP23008 = 0b000010000         # GPIO4
CS_TEMPERATURE = 0b010000000      # GPIO7
SAMPLE_PERIOD_S = 60


def configure_gpio(mcp, handle):
    all_pins = [f"GPIO{i}" for i in range(9)]
    mcp.Set_Gpio_Config(
        handle,
        constants.cfgSelector.MCP2210_VM_CONFIG,
        [constants.pGpioPinDes.MCP2210_PIN_DES_CS] * 9,                        # every pin is a chip select
        {pin: constants.dfltGpioOutput.MCP2210_HIGH for pin in all_pins},    # idle high
        {pin: constants.dfltGpioDir.MCP2210_OUTPUT for pin in all_pins},     # all outputs
        constants.rmtWkupEn.MCP2210_REMOTE_WAKEUP_DISABLED,
        constants.intPinMd.MCP2210_INT_MD_CNT_NONE,
        constants.spiBusRelEn.MCP2210_SPI_BUS_RELEASE_DISABLED,
    )


def print_spi_config(mcp, handle):
    config = mcp.get_spi_config(handle, constants.cfgSelector.MCP2210_NVRAM_CONFIG)
    print("Baud rate:", config["baudRate"])
    print("Idle CS Value:", config["idleCsVal"])
    print("Active CS Value:", config["activeCsVal"])
    print("CS->Data delay:", config["csToDataDly"])
    print("Data->CS delay:", config["dataToCsDly"])
    print("Data->Data delay:", config["dataToDataDly"])
    print("Transfer size:", config["txferSize"])
    print("SPI Mode:", config["spiMd"])


def setup_mcp23008(mcp, handle):
    """Make every MCP23008 pin an output and drive the pattern 0b10101010 (GP1, GP3, GP5, GP7 high)."""
    write_opcode = 0x40  # device address 0, write
    result = mcp.xfer_spi_data(handle, [write_opcode, 0x00, 0x00], BAUD_RATE, 3, CS_MCP23008)  # IODIR
    print(f"IODIR response: {result['data_rx']}")
    result = mcp.xfer_spi_data(handle, [write_opcode, 0x0A, 0b10101010], BAUD_RATE, 3, CS_MCP23008)  # OLAT
    print(f"OLAT response: {result['data_rx']}")


def log_temperature(mcp, handle):
    temperatures = deque()
    timestamps = deque()
    stop = threading.Event()
    start_time = time.time()
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], label="Temperature, °C")
    ax.set_xlabel("Time, s")
    ax.set_ylabel("Temperature, °C")
    ax.legend()
    ax.grid()

    def collect_data():
        while not stop.is_set():
            try:
                result = mcp.xfer_spi_data(handle, [0x00, 0x00], BAUD_RATE, 2, CS_TEMPERATURE)
                temperature = mcp.decode_temperature(result)
                current_time = time.time() - start_time
                temperatures.append(temperature)
                timestamps.append(current_time)
                with open(LOG_PATH, "a") as log_file:
                    log_file.write(f"{current_time},{temperature}\n")
            except Exception as e:
                print(f"Data collection error: {e}")
                stop.set()
            stop.wait(SAMPLE_PERIOD_S)

    data_thread = threading.Thread(target=collect_data, daemon=True)
    data_thread.start()
    try:
        # The plot has to be updated from the main thread.
        while not stop.is_set() and plt.fignum_exists(fig.number):
            line.set_data(list(timestamps), list(temperatures))
            ax.relim()
            ax.autoscale_view()
            plt.draw()
            plt.pause(0.1)
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        stop.set()
        data_thread.join()
        plt.close(fig)


def main():
    mcp = MCP2210()
    handle = mcp.open_device_by_index()
    try:
        print("NVRAM GPIO config:", mcp.get_gpio_config(handle, constants.cfgSelector.MCP2210_NVRAM_CONFIG))
        configure_gpio(mcp, handle)
        print("GPIO values:", bin(mcp.get_gpio_pin_val(handle)[1]))
        print_spi_config(mcp, handle)
        setup_mcp23008(mcp, handle)
        log_temperature(mcp, handle)
    finally:
        mcp.close_device(handle)


if __name__ == "__main__":
    main()
