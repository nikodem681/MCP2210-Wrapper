import scipy.io
import matplotlib.pyplot as plt
import pandas as pd

# Загружаем данные из .mat файла
data = scipy.io.loadmat("frequency_response.mat")

# Достаем массивы частоты и мощности
freqs = data["Freq_GHz"].flatten()  # Частоты в ГГц
powers = data["Power_dBm"].flatten()  # Мощность в dBm
powers_averaged = data["Power_dBm_averaged"].flatten()

print("Частоты:", freqs)
print("Мощность:", powers)

plt.figure(figsize=(10, 5))
plt.plot(freqs, powers, marker='o', linestyle='-')
plt.plot(freqs, powers_averaged, marker='o', linestyle='-')
plt.xlabel("Frequency (GHz)")
plt.ylabel("Power (dBm)")
plt.title("Frequency Response")
plt.grid(True)
plt.show()
print('wait')