from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PLOT_DIR = BASE_DIR / "plots"
PLOT_DIR.mkdir(exist_ok=True)

# Nur der dargestellte Bereich, keine Filterung der Daten.
ANZEIGE_MAX_MHZ = 50

OSZILLOSKOP_DATEIEN = {
    "5 MHz": DATA_DIR / "5Mhz" / "F0005CH1.CSV",
    "5,5 MHz": DATA_DIR / "5,5Mhz" / "F0006CH1.CSV",
    "6 MHz": DATA_DIR / "6Mhz" / "F0007CH1.CSV",
}


def tektronix_csv_laden(datei):
    """
    Tektronix-CSV:
    Spalte 4 = Zeit in s
    Spalte 5 = Spannung in V
    """
    daten = np.genfromtxt(
        datei,
        delimiter=",",
        usecols=(3, 4),
        dtype=float,
        invalid_raise=False,
        filling_values=np.nan,
    )

    zeit = daten[:, 0]
    spannung = daten[:, 1]

    gueltig = np.isfinite(zeit) & np.isfinite(spannung)
    zeit = zeit[gueltig]
    spannung = spannung[gueltig]

    sortierung = np.argsort(zeit)
    return zeit[sortierung], spannung[sortierung]


def fft_plotten(zeit, spannung, titel, dateiname):
    """
    Direkte FFT der vollständigen CSV:
    - kein Fenster
    - kein Zero-Padding
    - keine Filterung
    - keine Normierung auf dB
    """
    n = len(spannung)
    dt = np.mean(np.diff(zeit))

    fft_werte = np.fft.rfft(spannung)
    frequenzen = np.fft.rfftfreq(n, d=dt)

    # Einseitiges Amplitudenspektrum in Volt
    amplituden = np.abs(fft_werte) / n

    if n > 1:
        amplituden[1:-1] *= 2

    plt.figure(figsize=(9, 5))
    plt.stem(
        frequenzen / 1e6,
        amplituden,
        basefmt=" ",
    )

    plt.xlabel("Frequenz in MHz")
    plt.ylabel("Amplitude in V")
    plt.title(f"FFT der Oszilloskopaufnahme bei {titel}")
    plt.xlim(0, ANZEIGE_MAX_MHZ)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(dateiname, dpi=200)
    plt.close()

    frequenzabstand = frequenzen[1] - frequenzen[0]

    print(
        f"{titel}: {n} Messpunkte, "
        f"dt = {dt:.3e} s, "
        f"FFT-Abstand = {frequenzabstand / 1e6:.3f} MHz"
    )


def main():
    for titel, datei in OSZILLOSKOP_DATEIEN.items():
        zeit, spannung = tektronix_csv_laden(datei)

        name = (
            titel.replace(" ", "_")
            .replace(",", "_")
        )

        fft_plotten(
            zeit,
            spannung,
            titel,
            PLOT_DIR / f"fft_roh_{name}.png",
        )

    print(f"\nPlots gespeichert unter:\n{PLOT_DIR}")


if __name__ == "__main__":
    main()
