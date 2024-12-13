from mcp2210_wrapper import MCP2210
import constants
import time
import matplotlib.pyplot as plt
from collections import deque
import threading
import matplotlib.pyplot as plt
from collections import deque
import asyncio


# Путь к DLL
dll_path = "MCP2210/mcp2210_dll_um_x64.dll"
#
Connetced_MCP2210_devices = []
# Создаём экземпляр класса
mcp = MCP2210(dll_path)

try:
    handle = mcp.open_device_by_index()

    cfg_selector = constants.cfgSelector.MCP2210_NVRAM_CONFIG  # Селектор конфигурации
    gpio_config = mcp.get_gpio_config(handle, cfg_selector)
    # GPIO Pin Designation array
    gpio_pins = [
        constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO0
        constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO1
        constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO2
        constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO3
        constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO4
        constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO5
        constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO6
        constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO7
        constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO8
    ]

    # Default GPIO output values (example: all high)
    default_output = {
        "GPIO0": constants.dfltGpioOutput.MCP2210_HIGH,
        "GPIO1": constants.dfltGpioOutput.MCP2210_HIGH,
        "GPIO2": constants.dfltGpioOutput.MCP2210_HIGH,
        "GPIO3": constants.dfltGpioOutput.MCP2210_HIGH,
        "GPIO4": constants.dfltGpioOutput.MCP2210_HIGH,
        "GPIO5": constants.dfltGpioOutput.MCP2210_HIGH,
        "GPIO6": constants.dfltGpioOutput.MCP2210_HIGH,
        "GPIO7": constants.dfltGpioOutput.MCP2210_HIGH,
        "GPIO8": constants.dfltGpioOutput.MCP2210_HIGH
}

    # Default GPIO direction (example: all outputs)
    default_direction = {
        "GPIO0": constants.dfltGpioDir.MCP2210_OUPTUT,
        "GPIO1": constants.dfltGpioDir.MCP2210_OUPTUT,
        "GPIO2": constants.dfltGpioDir.MCP2210_OUPTUT,
        "GPIO3": constants.dfltGpioDir.MCP2210_OUPTUT,
        "GPIO4": constants.dfltGpioDir.MCP2210_OUPTUT,
        "GPIO5": constants.dfltGpioDir.MCP2210_OUPTUT,
        "GPIO6": constants.dfltGpioDir.MCP2210_OUPTUT,
        "GPIO7": constants.dfltGpioDir.MCP2210_OUPTUT,
        "GPIO8": constants.dfltGpioDir.MCP2210_OUPTUT
    }
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
    
    config = mcp.get_spi_config(handle, constants.cfgSelector.MCP2210_NVRAM_CONFIG)

    print("Скорость передачи:", config["baudRate"])
    print("Idle CS Value:", config["idleCsVal"])
    print("Active CS Value:", config["activeCsVal"])
    print("Задержка CS->Data:", config["csToDataDly"])
    print("Задержка Data->CS:", config["dataToCsDly"])
    print("Задержка между байтами:", config["dataToDataDly"])
    print("Размер передачи:", config["txferSize"])
    print("SPI Mode:", config["spiMd"])

    """
    Отправляет команды для настройки MCP23008 через MCP2210.

    Args:
        device: Экземпляр класса MCP2210.
        handle: Дескриптор устройства MCP2210.
    """
    # Установить GP0 как выход
    control_byte = 0x40  # Адрес устройства = 0, операция = запись
    reg_address = 0x00  # Адрес регистра IODIR
    data = 0x00  # GP0 = выход, остальные = вход
    baud_rate = 1000000  # Скорость передачи SPI (1 МГц)
    transfer_size = 3  # 3 байта: контрольный байт, адрес, данные
    cs_mask = 0b000010000  # GPIO4 используется как CS

    # Формируем команду для настройки IODIR
    data_tx = [control_byte, reg_address, data]
    result = mcp.xfer_spi_data(handle, data_tx, baud_rate, transfer_size, cs_mask)
    print(f"Ответ при настройке IODIR: {result['data_rx']}")

    # Установить GP0 в логическую единицу
    control_byte = 0x40  # Адрес устройства = 0, операция = запись
    reg_address = 0x0A  # Адрес регистра OLAT
    data = 0b10101010  # GP0 = 1, остальные = 0

    # Формируем команду для настройки OLAT
    data_tx = [control_byte, reg_address, data]
    result = mcp.xfer_spi_data(handle, data_tx, baud_rate, transfer_size, cs_mask)
    print(f"Ответ при настройке OLAT: {result['data_rx']}")



     # Test temperature
    start_time = time.time()
    stop_thread = threading.Event() 

    temperatures = deque(maxlen=90000000000)  # Храним последние 100 значений температуры
    timestamps = deque(maxlen=90000000000)   # Храним соответствующие временные метки
    # Инициализация графика
    plt.ion()  # Включаем интерактивный режим
    fig, ax = plt.subplots()
    line, = ax.plot([], [], label="Температура, °C")
    ax.set_xlabel("Время, с")
    ax.set_ylabel("Температура, °C")
    ax.legend()
    ax.grid()

    def collect_data():
        """Функция для сбора данных температуры в отдельном потоке."""
        global temperatures, timestamps
        while not stop_thread.is_set():
            try:
                cs_mask = 0b010000000  # GPIO7 используется как CS
                transfer_size = 2
                data_tx = [0x00, 0x00]

                # Получение данных с устройства (симуляция реального устройства)
                result = mcp.xfer_spi_data(handle, data_tx, baud_rate, transfer_size, cs_mask)
                temperature = mcp.decode_temperature(result)

                # Обновляем данные
                current_time = time.time() - start_time
                temperatures.append(temperature)
                timestamps.append(current_time)

                # Сохраняем данные в файл
                with open("temperature_log.csv", "a") as log_file:
                    log_file.write(f"{current_time},{temperature}\n")

                # Пауза между измерениями
                time.sleep(60)  # 60 секунд
            except Exception as e:
                print(f"Ошибка сбора данных: {e}")
                stop_thread.set()


    def update_graph():
        """Функция для обновления графика в главном потоке."""
        while not stop_thread.is_set():
            try:
                # Обновляем данные графика
                line.set_data(timestamps, temperatures)
                ax.relim()
                ax.autoscale_view()

                plt.draw()
                plt.pause(0.1)  # Обновляем график каждые 0.1 секунды
            except Exception as e:
                print(f"Ошибка обновления графика: {e}")
                stop_thread.set()


    # Запускаем поток для сбора данных
    data_thread = threading.Thread(target=collect_data, daemon=True)
    data_thread.start()

    try:
        # Главный поток занимается обновлением графика
        update_graph()
    except KeyboardInterrupt:
        print("Выход из программы")
        stop_thread.set()  # Устанавливаем флаг остановки
        data_thread.join()  # Ждём завершения потока сбора данных
        plt.close()  # Закрываем график

    mcp.close_device(handle)
except Exception as e:
    print(f"Ошибка: {e}")