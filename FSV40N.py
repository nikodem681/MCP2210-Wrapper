import pyvisa

def SA_init(IP_address: str):
    try:
        rm = pyvisa.ResourceManager()
        instr = rm.open_resource(f"TCPIP::{IP_address}::INSTR")
        print(instr.query("*IDN?")) 
        return instr
    except Exception as e:
        print(f"Error: {e}")

def SA_set_ref_level(instr, ref_level: float):
    """
    Sets the Reference Level (REF LEVEL) on the spectrum analyzer.

    :param instr: An open pyvisa.resources.Resource object (spectrum analyzer instance)
    :param ref_level: Reference Level in dBm (e.g., 0, -10, -30)
    """
    try:
        # Send SCPI command to set the Reference Level
        instr.write(f":DISP:TRAC:Y:RLEV {ref_level}")

        # Query the current Reference Level to verify the change
        current_ref_level = instr.query(":DISP:TRAC:Y:RLEV?")
        print(f"REF LEVEL set to: {current_ref_level.strip()} dBm")

    except Exception as e:
        print(f"Error: {e}")

def SA_get_ref_level(instr) -> float:
    """
    Retrieves the current Reference Level (REF LEVEL) from the spectrum analyzer.

    :param instr: An open pyvisa.resources.Resource object (spectrum analyzer instance)
    :return: The current Reference Level in dBm as a float
    """
    try:
        # Query the current Reference Level
        ref_level = instr.query(":DISP:TRAC:Y:RLEV?")

        # Convert the response to a float and return
        return float(ref_level.strip())

    except Exception as e:
        print(f"Error retrieving REF LEVEL: {e}")
        return None  # Return None in case of an error

def SA_set_attenuator(instr, att_level: float):
    """
    Sets the input attenuator level on the spectrum analyzer.

    :param instr: An open pyvisa.resources.Resource object (spectrum analyzer instance)
    :param att_level: Attenuation level in dB (e.g., 0, 10, 20)
    """
    try:
        # Send SCPI command to set the attenuation level
        instr.write(f":INP:ATT {att_level}")

        # Verify the change
        current_att = instr.query(":INP:ATT?")
        print(f"Attenuator set to: {current_att.strip()} dB")

    except Exception as e:
        print(f"Error setting attenuator: {e}")

def SA_get_attenuator(instr) -> float:
    """
    Retrieves the current input attenuator level from the spectrum analyzer.

    :param instr: An open pyvisa.resources.Resource object (spectrum analyzer instance)
    :return: The current attenuator level in dB as a float
    """
    try:
        # Query the current attenuation level
        att_level = instr.query(":INP:ATT?")

        # Convert the response to a float and return
        return float(att_level.strip())

    except Exception as e:
        print(f"Error retrieving attenuator level: {e}")
        return None  # Return None in case of an error


def SA_set_start_freq(instr, start_freq: float):
    """
    Sets the start frequency on the spectrum analyzer.

    :param instr: An open pyvisa.resources.Resource object (spectrum analyzer instance)
    :param start_freq: Start frequency in Hz (e.g., 1e6 for 1 MHz, 1e9 for 1 GHz)
    """
    try:
        instr.write(f":SENS:FREQ:START {start_freq}")
        print(f"Start frequency set to: {start_freq} Hz")

    except Exception as e:
        print(f"Error setting start frequency: {e}")

def SA_set_stop_freq(instr, stop_freq: float):
    """
    Sets the stop frequency on the spectrum analyzer.

    :param instr: An open pyvisa.resources.Resource object (spectrum analyzer instance)
    :param stop_freq: Stop frequency in Hz (e.g., 1e6 for 1 MHz, 1e9 for 1 GHz)
    """
    try:
        instr.write(f":SENS:FREQ:STOP {stop_freq}")
        print(f"Stop frequency set to: {stop_freq} Hz")

    except Exception as e:
        print(f"Error setting stop frequency: {e}")

def SA_get_start_freq(instr) -> float:
    """
    Retrieves the current start frequency from the spectrum analyzer.

    :param instr: An open pyvisa.resources.Resource object (spectrum analyzer instance)
    :return: The current start frequency in Hz as a float
    """
    try:
        start_freq = instr.query(":SENS:FREQ:START?")
        return float(start_freq.strip())

    except Exception as e:
        print(f"Error retrieving start frequency: {e}")
        return None  # Return None in case of an error

def SA_get_stop_freq(instr) -> float:
    """
    Retrieves the current stop frequency from the spectrum analyzer.

    :param instr: An open pyvisa.resources.Resource object (spectrum analyzer instance)
    :return: The current stop frequency in Hz as a float
    """
    try:
        stop_freq = instr.query(":SENS:FREQ:STOP?")
        return float(stop_freq.strip())

    except Exception as e:
        print(f"Error retrieving stop frequency: {e}")
        return None  # Return None in case of an error

def convert_to_Hz(value: float, unit: str) -> float:
    """
    Converts a given frequency value to Hz based on the specified unit.

    :param value: The numerical value of the frequency (e.g., 5, 10, 40)
    :param unit: The frequency unit as a string ('Hz', 'kHz', 'MHz', 'GHz')
    :return: The frequency converted to Hz as a float
    """
    unit_multipliers = {
        "Hz": 1,
        "kHz": 1e3,
        "MHz": 1e6,
        "GHz": 1e9
    }

    try:
        return value * unit_multipliers[unit]
    except KeyError:
        raise ValueError(f"Invalid unit '{unit}'. Use 'Hz', 'kHz', 'MHz', or 'GHz'.")


def set_signal_generator(instrument, channel, freq, power):
    """
    Устанавливает частоту и мощность на указанном канале генератора сигналов.
    
    :param instrument: SCPI-сессия или объект управления устройством
    :param channel: Номер канала (1 или 2)
    :param freq: Частота в Гц (float или int)
    :param power: Мощность в дБм (float или int)
    """
    instrument.write(f"SOUR{channel}:FREQ {freq}")  # Установка частоты
    instrument.write(f"SOUR{channel}:POW {power}")  # Установка мощности

def SA_set_marker_max(instr) -> float:
    """
    Sets marker 1 to the maximum peak and retrieves its frequency and amplitude.

    :param instr: An open pyvisa.resources.Resource object (spectrum analyzer instance)
    :return: A tuple (frequency in Hz, amplitude in dBm) or None if an error occurs
    """
    try:
        instr.write(":CALC:MARK1:MAX")  # Установить маркер 1 на максимум
        time.sleep(0.1)
        freq = instr.query(":CALC:MARK1:X?")  # Получить частоту маркера
        ampl = instr.query(":CALC:MARK1:Y?")  # Получить амплитуду маркера

        return float(freq.strip()), float(ampl.strip())  # Вернуть данные маркера

    except Exception as e:
        print(f"Error setting marker to max: {e}")
        return None

def SA_is_sweep_complete(instr) -> bool:
    """
    Проверяет, завершена ли развертка анализатора спектра.

    :param instr: Объект pyvisa.resources.Resource (спектроанализатор)
    :return: True, если развертка завершена, False, если нет
    """
    try:
        status = int(instr.query(":STAT:OPER:COND?"))  # Запрос состояния развертки
        return status == 0  # Если статус 0 — развертка завершена

    except Exception as e:
        print(f"Ошибка при проверке завершения развертки: {e}")
        return False
    
def set_sweep_points(instr, points):
    """
    Устанавливает количество точек в развертке анализатора спектра.

    :param instr: Объект pyvisa.resources.Resource (спектроанализатор)
    :param points: Количество точек (обычно от 101 до 10001)
    """
    instr.write(f"SWEep:POINts {points}")

def enable_manual_sweep(instr):
    """
    Переключает анализатор спектра в ручной режим развертки.
    """
    instr.write("INITiate:CONTinuous OFF")  # Отключить авторазвертку

def start_manual_sweep(instr):
    """
    Запускает развертку вручную (однократный запуск).
    """
    instr.write("INITiate:IMMediate")  # Запустить развертку

def single_sweep(instr):
    """
    Выполняет однократную развертку на анализаторе спектра и ждет её завершения.
    
    :param instr: Объект pyvisa.resources.Resource (спектроанализатор)
    """
    instr.write("INITiate:CONTinuous OFF")  # Отключить авторазвертку
    instr.write("INITiate:IMMediate")       # Запустить развертку один раз

    # Ждем, пока развертка не завершится
    while True:
        status = int(instr.query(":STATus:OPERation:CONDition?").strip())
        if status == 0:  # Развертка завершена
            break
        time.sleep(0.1)  # Ждать 100 мс перед следующим запросом

def configure_sa(instr, rbw=10e3, vbw=10e3, detector="POS", average=False):
    """
    Устанавливает основные параметры анализатора спектра (SA) для быстрого измерения.

    :param instr: Объект pyvisa.resources.Resource (анализатор спектра)
    :param rbw: Полоса разрешения (RBW) в Гц, по умолчанию 100 кГц
    :param vbw: Полоса видеофильтра (VBW) в Гц, по умолчанию 100 кГц
    :param detector: Тип детектора ("POS" - положительный, "SAMP" - выборка, "NORM" - нормальный)
    :param average: Включить ли усреднение (True/False)
    """
    instr.write(":FREQ:SPAN 1e6")  # Устанавливаем Zero Span (режим одной точки)
    instr.write(f"BANDwidth:RES {rbw}")  # Полоса разрешения (RBW)
    instr.write(f"BANDwidth:VID {vbw}")  # Полоса видеофильтра (VBW)
    instr.write("INITiate:CONTinuous OFF")  # Отключаем автоматическую развертку

def measure_single_frequency(instr, freq_hz):
    """
    Измеряет мощность на одной частоте.
    """
    instr.write(f"FREQ:CENT {freq_hz}")  # Устанавливаем центральную частоту
    instr.write("INITiate:IMMediate")    # Запускаем измерение
    time.sleep(0.1)  # Ждем 50 мс перед повторным запросом
    # Ждем завершения измерения
    while True:
        status = int(instr.query(":STATus:OPERation:CONDition?").strip())
        if status == 0:  # Развертка завершена
            break
        time.sleep(0.05)  # Ждем 50 мс перед повторным запросом
        print("SA is not ready, sleep...")
    instr.write('CALC:MARK1:MAX')
    time.sleep(0.01)  # Ждем 50 мс перед повторным запросом
    power = instr.query("CALC:MARK1:Y?")
    #power = instr.query("READ:POW?")  # Читаем измеренное значение мощности
    return float(power.strip())  # Возвращаем мощность в дБм

def measure_average_power(instrument, frequency, num_measurements=8):
    """
    Функция для измерения мощности на заданной частоте несколько раз и вычисления среднего значения.
    
    :param instrument: Объект прибора (например, pyvisa.Resource)
    :param frequency: Частота, на которой выполняется измерение (в Гц)
    :param num_measurements: Количество измерений (по умолчанию 8)
    :return: Среднее арифметическое значение мощности
    """
    total_power = 0.0

    for i in range(num_measurements):
        power = measure_single_frequency(instrument, frequency)
        print(f"Измерение {i + 1}: {power} дБм")
        total_power += power

    average_power = total_power / num_measurements
    return average_power

def get_SA_device_info(device):
    """Retrieve SCPI device information including Name, SPAN, RBW, BWB, OUTREF, and ATT.""" 
    try:
        # Open connection to the SCPI device

        # Query device info
        info = {
            "Name": device.query("*IDN?").strip(),
            "SPAN": device.query("FREQ:SPAN?").strip(),
            "RBW": device.query("BAND:RES?").strip(),
            "BWB": device.query("BAND?").strip(),  # BWB might refer to overall bandwidth
            "OUTREF": device.query(":DISP:TRAC:Y:RLEV?").strip(),  # Corrected command
            "ATT": device.query("INP:ATT?").strip(),
        }
        return info

    except Exception as e:
        return {"Error": str(e)}

def check_and_set_yig_filter(instr, freq):
    """Проверяет частоту и управляет YIG-фильтром на R&S FSP."""
    
    # Запрос текущей частоты
    freq_hz = freq # Получаем частоту в Гц
    
    # Запрос текущего состояния YIG-фильтра
    yig_state = instr.query(":INP:FILT:YIG?").strip()  # 'ON' или 'OFF'
    
    if freq_hz >= 29e9 and yig_state != "OFF":  # Частота ≥ 29 ГГц → фильтр OFF
        instr.write(":INP:FILT:YIG OFF")
        print("YIG Filter turned OFF (Frequency >= 29 GHz)")

    elif freq_hz < 29e9 and yig_state != "ON":  # Частота < 29 ГГц → фильтр ON
        instr.write(":INP:FILT:YIG ON")
        print("YIG Filter turned ON (Frequency < 29 GHz)")




########################################################################################################################
#FSV40_N = SA_init("192.168.2.165")
#SA_set_start_freq(FSV40_N, convert_to_Hz(1, "GHz"))
#SA_set_stop_freq(FSV40_N, convert_to_Hz(2, "GHz"))
import time
import pandas as pd
import matplotlib.pyplot as plt
import ctypes

data = []

try:
    # Load the libusb DLL
    libusb = ctypes.cdll.LoadLibrary("libusb-1.0.dll")
    print("libusb DLL loaded successfully!")
except Exception as e:
    print(f"Failed to load libusb DLL: {e}")
rm = pyvisa.ResourceManager()

device_id = "USB0::0x03EB::0xAFFF::3E7-0C4L20001-1115::INSTR"  # Формат NI-VISA
try:
    ANAPICO = rm.open_resource(device_id)
    print(f"Подключено к: {ANAPICO.query('*IDN?')}")
except Exception as e:
    print(f"Ошибка подключения: {e}")

#FSV40_N = SA_init("192.168.2.165")
FSV40_N = SA_init("192.168.2.154") #bad rohde shwarz


ANAPICO.write("FREQ 1e9")
ANAPICO.write("POW -10")
ANAPICO.write("OUTP OFF")
ANAPICO.write("OUTP2 ON")

import time
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io
from datetime import datetime
import scipy.io
SA_set_attenuator(FSV40_N, 40)
SA_set_ref_level(FSV40_N, 20)
set_sweep_points(FSV40_N, 300)
enable_manual_sweep(FSV40_N)
configure_sa(FSV40_N)
info = get_SA_device_info(FSV40_N)
print("\n--- Spectrum Analyzer Info ---")
for key, value in info.items():
    print(f"{key}: {value}")
    
data = {"Freq_GHz": [], "Power_dBm": [],"Power_dBm_averaged": []}
for freq in range(int(0.7e9), int(40e9), int(0.1e9)):  # Шаг 0.1 ГГц
    set_signal_generator(ANAPICO, 2, freq, 0)  # Установка генератора
    time.sleep(0.1)
    
    # Измерение мощности на заданной частоте
    check_and_set_yig_filter(FSV40_N, freq)
    power = measure_single_frequency(FSV40_N, freq)
    power_averaged = measure_average_power(FSV40_N, freq)

    # Вывод результатов в консоль
    print(f"Freq is {freq / 1e9} GHz, Power is {power} dBm")

    # Добавление данных в список
    data["Freq_GHz"].append(freq / 1e9)  # Конвертируем в ГГц
    data["Power_dBm"].append(power)
    #data["Power_dBm_averaged"].append(power)
    data["Power_dBm_averaged"].append(power_averaged)

# Создание DataFrame для удобства
df = pd.DataFrame(data)
# Сохранение данных в .mat
timestamp = datetime.now().strftime("%m_%d_%H_%M")
filename = f"frequency_response_{timestamp}.mat"
scipy.io.savemat(filename, data)

#Convert info dictionary to a format suitable for .mat files
mat_data = {
    "measurement_data": {col: df[col].values.reshape(-1, 1) for col in df.columns},  # Сохраняем столбцами
    "device_info": info
}

scipy.io.savemat(filename, mat_data)
print("Данные сохранены в frequency_response.mat")

# Построение графика
plt.figure(figsize=(10, 5))
plt.plot(df["Freq_GHz"], df["Power_dBm"], marker='o', linestyle='-')
plt.plot(df["Freq_GHz"], df["Power_dBm_averaged"], marker='o', linestyle='-')
plt.xlabel("Frequency (GHz)")
plt.ylabel("Power (dBm)")
plt.title("Frequency Response")
plt.grid(True)
plt.show()

print("График построен, данные сохранены!")

