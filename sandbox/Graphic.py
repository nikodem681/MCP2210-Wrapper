"""
Plot a frequency response saved by frequency_response.py.

    python sandbox/Graphic.py [file.mat]

Without an argument, plots the newest .mat file in data/. Reads both the
current layout (a measurement_data struct) and the older one with
Freq_GHz / Power_dBm / Power_dBm_averaged at the top level.
"""
import glob
import os
import sys

import matplotlib.pyplot as plt
import scipy.io

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_response(path):
    data = scipy.io.loadmat(path)
    if "measurement_data" in data:
        data = data["measurement_data"][0, 0]
    return (data["Freq_GHz"].flatten(),
            data["Power_dBm"].flatten(),
            data["Power_dBm_averaged"].flatten())


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        files = glob.glob(os.path.join(REPO_ROOT, "data", "*.mat"))
        if not files:
            sys.exit("No .mat files in data/; pass a file name.")
        path = max(files, key=os.path.getmtime)

    freqs, powers, powers_averaged = load_response(path)
    print("File:", path)
    print("Frequencies, GHz:", freqs)
    print("Power, dBm:", powers)

    plt.figure(figsize=(10, 5))
    plt.plot(freqs, powers, marker='o', linestyle='-')
    plt.plot(freqs, powers_averaged, marker='o', linestyle='-')
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Power (dBm)")
    plt.title("Frequency Response")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
