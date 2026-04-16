import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# Daten einlesen
# KiCad Daten: v-sweep, I(Vdd1), V(/Vg)
data_kicad = pd.read_csv('data/ANS_Uebung1_kicad.csv', delimiter=';', decimal=',')
v_sweep_kicad = data_kicad['v-sweep'].values
I_Vdd1_kicad = data_kicad['I(Vdd1)'].values
V_Vg_kicad = data_kicad['V(/Vg)'].values

# Ngspice Daten: v-sweep, V(/Vg), ?, I(Vdd1)
data_ngspice = np.loadtxt('data/ANS_Uebung1_ngspice.csv')
v_sweep_ngspice = data_ngspice[:, 0]
V_Vg_ngspice = data_ngspice[:, 1]
I_Vdd1_ngspice = data_ngspice[:, 3]  # Annahme: vierte Spalte ist I(Vdd1)

# Vergleich: Plot I(Vdd1) vs v-sweep für beide
plt.figure(figsize=(10, 6))
plt.plot(v_sweep_kicad, I_Vdd1_kicad, label='KiCad I(Vdd1)', marker='o')
plt.plot(v_sweep_ngspice, I_Vdd1_ngspice, label='Ngspice I(Vdd1)', marker='x')
plt.xlabel('v-sweep (V)')
plt.ylabel('I(Vdd1) (A)')
plt.title('Vergleich von I(Vdd1) aus KiCad und Ngspice')
plt.legend()
plt.grid(True)
plt.show()

# Numerischer Vergleich: Differenz berechnen
diff_I = I_Vdd1_kicad - I_Vdd1_ngspice
plt.figure(figsize=(10, 6))
plt.plot(v_sweep_kicad, diff_I, label='Differenz I(Vdd1) KiCad - Ngspice', marker='s')
plt.xlabel('v-sweep (V)')
plt.ylabel('Differenz I(Vdd1) (A)')
plt.title('Differenz zwischen KiCad und Ngspice I(Vdd1)')
plt.legend()
plt.grid(True)
plt.show()

# Ausgabe der maximalen Differenz
max_diff = np.max(np.abs(diff_I))
print(f'Maximale absolute Differenz in I(Vdd1): {max_diff} A')

