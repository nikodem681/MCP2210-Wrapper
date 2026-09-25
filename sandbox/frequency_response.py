"""
Frequency response sweep: Anapico signal generator -> R&S FSV40-N spectrum analyzer.

Steps the generator over a frequency range, reads the analyzer's peak power at
each point, saves the result to data/<prefix>_<timestamp>.mat and plots it.

The defaults are the 0.7-40 GHz sweep. The low-frequency Anapico run is:

    python sandbox/frequency_response.py --start 0.3e6 --stop 1.1e6 --step 0.1e6 \\
        --power -20 --no-yig --no-average --toggle-output \\
        --prefix Anapico_1MHz_200MHz_30db_att
"""
import argparse
import ctypes
import os
import sys
import time
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import pyvisa
import scipy.io

from instrumentation.SA.FSV40N import (
    SA_init,
    SA_set_attenuator,
    SA_set_ref_level,
    check_and_set_yig_filter,
    configure_sa,
    enable_manual_sweep,
    get_SA_device_info,
    measure_average_power,
    measure_single_frequency,
    set_signal_generator,
    set_sweep_points,
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIBUSB_PATH = os.path.join(REPO_ROOT, "instrumentation", "PCBs", "libusb-1.0.dll")

DEFAULT_SA_IP = "192.168.2.165"  # 192.168.2.154 is the faulty R&S unit
DEFAULT_GENERATOR = "USB0::0x03EB::0xAFFF::3E7-0C4L20001-1115::INSTR"  # NI-VISA format

SA_ATTENUATION_DB = 40
SA_REF_LEVEL_DBM = 20
SA_SWEEP_POINTS = 300


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sa-ip", default=DEFAULT_SA_IP,
                        help="spectrum analyzer IP address (default: %(default)s)")
    parser.add_argument("--generator", default=DEFAULT_GENERATOR,
                        help="VISA resource of the signal generator (default: %(default)s)")
    parser.add_argument("--channel", type=int, default=2,
                        help="generator channel (default: %(default)s)")
    parser.add_argument("--start", type=float, default=0.7e9,
                        help="start frequency, Hz (default: %(default)g)")
    parser.add_argument("--stop", type=float, default=40e9,
                        help="stop frequency, Hz, exclusive (default: %(default)g)")
    parser.add_argument("--step", type=float, default=0.1e9,
                        help="frequency step, Hz (default: %(default)g)")
    parser.add_argument("--power", type=float, default=0,
                        help="generator power, dBm (default: %(default)g)")
    parser.add_argument("--no-yig", action="store_true",
                        help="don't switch the YIG filter at 29 GHz")
    parser.add_argument("--no-average", action="store_true",
                        help="skip the averaged reading; Power_dBm_averaged repeats Power_dBm")
    parser.add_argument("--toggle-output", action="store_true",
                        help="turn the generator output on before the sweep and off after it")
    parser.add_argument("--prefix", default="frequency_response",
                        help="output file name prefix (default: %(default)s)")
    parser.add_argument("--out-dir", default=os.path.join(REPO_ROOT, "data"),
                        help="output directory (default: <repo>/data)")
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        ctypes.cdll.LoadLibrary(LIBUSB_PATH)
        print("libusb DLL loaded successfully!")
    except Exception as e:
        print(f"Failed to load libusb DLL: {e}")

    rm = pyvisa.ResourceManager()
    try:
        generator = rm.open_resource(args.generator)
        print(f"Connected to: {generator.query('*IDN?')}")
    except Exception as e:
        sys.exit(f"Failed to connect to the signal generator: {e}")

    sa = SA_init(args.sa_ip)
    if sa is None:
        sys.exit(f"Failed to connect to the spectrum analyzer at {args.sa_ip}")

    SA_set_attenuator(sa, SA_ATTENUATION_DB)
    SA_set_ref_level(sa, SA_REF_LEVEL_DBM)
    set_sweep_points(sa, SA_SWEEP_POINTS)
    enable_manual_sweep(sa)
    configure_sa(sa)
    info = get_SA_device_info(sa)
    print("\n--- Spectrum Analyzer Info ---")
    for key, value in info.items():
        print(f"{key}: {value}")

    data = {"Freq_GHz": [], "Power_dBm": [], "Power_dBm_averaged": []}
    if args.toggle_output:
        generator.write(f"OUTP{args.channel} ON")
    try:
        for freq in range(int(args.start), int(args.stop), int(args.step)):
            set_signal_generator(generator, args.channel, freq, args.power)
            time.sleep(0.1)

            if not args.no_yig:
                check_and_set_yig_filter(sa, freq)
            power = measure_single_frequency(sa, freq)
            power_averaged = power if args.no_average else measure_average_power(sa, freq)

            print(f"Freq is {freq / 1e9} GHz, Power is {power} dBm")
            data["Freq_GHz"].append(freq / 1e9)
            data["Power_dBm"].append(power)
            data["Power_dBm_averaged"].append(power_averaged)
    finally:
        if args.toggle_output:
            generator.write(f"OUTP{args.channel} OFF")

    df = pd.DataFrame(data)
    os.makedirs(args.out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%m_%d_%H_%M")
    filename = os.path.join(args.out_dir, f"{args.prefix}_{timestamp}.mat")
    scipy.io.savemat(filename, {
        "measurement_data": {col: df[col].values.reshape(-1, 1) for col in df.columns},
        "device_info": info,
    })
    print(f"Data saved to {filename}")

    plt.figure(figsize=(10, 5))
    plt.plot(df["Freq_GHz"], df["Power_dBm"], marker='o', linestyle='-')
    plt.plot(df["Freq_GHz"], df["Power_dBm_averaged"], marker='o', linestyle='-')
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Power (dBm)")
    plt.title("Frequency Response")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
