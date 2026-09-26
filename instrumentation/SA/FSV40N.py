import time

import pyvisa

def SA_init(IP_address: str):
    """
    Open the spectrum analyzer over LAN (VISA TCPIP) and print its *IDN?.

    :param IP_address: analyzer IP address
    :return: the open pyvisa resource, or None if the connection failed
    """
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
    Set the frequency and power of one signal generator channel.

    :param instrument: open pyvisa resource of the generator
    :param channel: channel number (1 or 2)
    :param freq: frequency in Hz
    :param power: power in dBm
    """
    instrument.write(f"SOUR{channel}:FREQ {freq}")
    instrument.write(f"SOUR{channel}:POW {power}")

def SA_set_marker_max(instr):
    """
    Sets marker 1 to the maximum peak and retrieves its frequency and amplitude.

    :param instr: An open pyvisa.resources.Resource object (spectrum analyzer instance)
    :return: A tuple (frequency in Hz, amplitude in dBm) or None if an error occurs
    """
    try:
        instr.write(":CALC:MARK1:MAX")
        time.sleep(0.1)
        freq = instr.query(":CALC:MARK1:X?")
        ampl = instr.query(":CALC:MARK1:Y?")

        return float(freq.strip()), float(ampl.strip())

    except Exception as e:
        print(f"Error setting marker to max: {e}")
        return None

def SA_is_sweep_complete(instr) -> bool:
    """
    Check whether the analyzer sweep has finished.

    :param instr: open pyvisa resource of the spectrum analyzer
    :return: True if the sweep is complete, False otherwise
    """
    try:
        status = int(instr.query(":STAT:OPER:COND?"))
        return status == 0  # 0: no operation running

    except Exception as e:
        print(f"Error checking sweep status: {e}")
        return False

def set_sweep_points(instr, points):
    """
    Set the number of sweep points.

    :param instr: open pyvisa resource of the spectrum analyzer
    :param points: number of points (typically 101 to 10001)
    """
    instr.write(f"SWEep:POINts {points}")

def enable_manual_sweep(instr):
    """
    Switch the analyzer to single (manually triggered) sweeps.
    """
    instr.write("INITiate:CONTinuous OFF")

def start_manual_sweep(instr):
    """
    Trigger one sweep.
    """
    instr.write("INITiate:IMMediate")

def single_sweep(instr):
    """
    Run one sweep and wait for it to finish.

    :param instr: open pyvisa resource of the spectrum analyzer
    """
    instr.write("INITiate:CONTinuous OFF")
    instr.write("INITiate:IMMediate")

    while True:
        status = int(instr.query(":STATus:OPERation:CONDition?").strip())
        if status == 0:  # sweep finished
            break
        time.sleep(0.1)

def configure_sa(instr, rbw=10e3, vbw=10e3, detector=None, average=False):
    """
    Set up the analyzer for fast single-frequency measurements: 1 MHz span,
    the given RBW/VBW, single sweeps.

    :param instr: open pyvisa resource of the spectrum analyzer
    :param rbw: resolution bandwidth in Hz (default 10 kHz)
    :param vbw: video bandwidth in Hz (default 10 kHz)
    :param detector: detector to select ("POS", "SAMP", "RMS", ...); None leaves it unchanged
    :param average: turn trace averaging on
    """
    instr.write(":FREQ:SPAN 1e6")
    instr.write(f"BANDwidth:RES {rbw}")
    instr.write(f"BANDwidth:VID {vbw}")
    if detector is not None:
        instr.write(f"DET {detector}")
    if average:
        instr.write("AVER:STAT ON")
    instr.write("INITiate:CONTinuous OFF")

def measure_single_frequency(instr, freq_hz):
    """
    Measure the peak power around one frequency.

    :param instr: open pyvisa resource of the spectrum analyzer
    :param freq_hz: center frequency in Hz
    :return: marker 1 power in dBm
    """
    instr.write(f"FREQ:CENT {freq_hz}")
    instr.write("INITiate:IMMediate")
    time.sleep(0.1)
    # Wait for the sweep to finish
    while True:
        status = int(instr.query(":STATus:OPERation:CONDition?").strip())
        if status == 0:  # sweep finished
            break
        time.sleep(0.05)
        print("SA is not ready, sleep...")
    instr.write('CALC:MARK1:MAX')
    time.sleep(0.01)
    power = instr.query("CALC:MARK1:Y?")
    return float(power.strip())

def measure_average_power(instrument, frequency, num_measurements=8):
    """
    Measure the power at one frequency several times and return the mean.

    :param instrument: open pyvisa resource of the spectrum analyzer
    :param frequency: frequency in Hz
    :param num_measurements: number of measurements (default 8)
    :return: mean power in dBm
    """
    total_power = 0.0

    for i in range(num_measurements):
        power = measure_single_frequency(instrument, frequency)
        print(f"Measurement {i + 1}: {power} dBm")
        total_power += power

    return total_power / num_measurements

def get_SA_device_info(device):
    """Retrieve SCPI device information including Name, SPAN, RBW, BWB, OUTREF, and ATT."""
    try:
        info = {
            "Name": device.query("*IDN?").strip(),
            "SPAN": device.query("FREQ:SPAN?").strip(),
            "RBW": device.query("BAND:RES?").strip(),
            "BWB": device.query("BAND?").strip(),  # BWB might refer to overall bandwidth
            "OUTREF": device.query(":DISP:TRAC:Y:RLEV?").strip(),
            "ATT": device.query("INP:ATT?").strip(),
        }
        return info

    except Exception as e:
        return {"Error": str(e)}

def check_and_set_yig_filter(instr, freq):
    """Turn the YIG preselector off at and above 29 GHz and on below it (R&S FSP/FSV)."""
    yig_state = instr.query(":INP:FILT:YIG?").strip()  # 'ON' or 'OFF' (some firmware answers 1/0)

    if freq >= 29e9 and yig_state not in ("OFF", "0"):
        instr.write(":INP:FILT:YIG OFF")
        print("YIG Filter turned OFF (Frequency >= 29 GHz)")

    elif freq < 29e9 and yig_state not in ("ON", "1"):
        instr.write(":INP:FILT:YIG ON")
        print("YIG Filter turned ON (Frequency < 29 GHz)")
