from pathlib import Path
import csv

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Pfade und Zuordnung der Dateien
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PLOT_DIR = BASE_DIR / "plots"
PLOT_DIR.mkdir(exist_ok=True)

N_PERIODS = 3

MESSUNGEN = {
    "5 MHz": {
        "frequenz": 5.0e6,
        "simulation": DATA_DIR / "FM_VCO_689V.csv",
        "oszilloskop": DATA_DIR / "5Mhz" / "F0005CH1.CSV",
    },
    "5,5 MHz": {
        "frequenz": 5.5e6,
        "simulation": DATA_DIR / "FM_VCO_606V.csv",
        "oszilloskop": DATA_DIR / "5,5Mhz" / "F0006CH1.CSV",
    },
    "6 MHz": {
        "frequenz": 6.0e6,
        "simulation": DATA_DIR / "FM_VCO_533V.csv",
        "oszilloskop": DATA_DIR / "6Mhz" / "F0007CH1.CSV",
    },
}


# ============================================================
# CSV-Dateien einlesen
# ============================================================

def trennzeichen_erkennen(datei):
    text = datei.read_text(
        encoding="utf-8-sig",
        errors="ignore"
    )[:5000]

    try:
        return csv.Sniffer().sniff(
            text,
            delimiters=",;\t"
        ).delimiter
    except csv.Error:
        return ","


def in_zahlen_umwandeln(spalte, trennzeichen):
    werte = spalte.astype(str).str.strip()

    if trennzeichen != ",":
        werte = werte.str.replace(",", ".", regex=False)

    return pd.to_numeric(werte, errors="coerce")


def tektronix_csv_laden(datei, trennzeichen):
    """
    Liest das CSV-Format des Tektronix TBS1052B-EDU ein.

    In diesen Dateien stehen:
        Spalte 0: Bezeichnung der Metadaten
        Spalte 1: Wert der Metadaten
        Spalte 2: leer
        Spalte 3: Zeit in Sekunden
        Spalte 4: Spannung in Volt
    """
    roh = pd.read_csv(
        datei,
        sep=trennzeichen,
        header=None,
        engine="python",
        on_bad_lines="skip",
        encoding_errors="ignore",
        dtype=str,
    )

    if roh.shape[1] < 5:
        raise ValueError(
            f"{datei.name} besitzt nur {roh.shape[1]} Spalten. "
            "Für das erwartete Tektronix-Format werden mindestens "
            "fünf Spalten benötigt."
        )

    zeit = in_zahlen_umwandeln(
        roh.iloc[:, 3],
        trennzeichen
    )

    signal = in_zahlen_umwandeln(
        roh.iloc[:, 4],
        trennzeichen
    )

    gueltig = zeit.notna() & signal.notna()

    zeit = zeit[gueltig].to_numpy(dtype=float)
    signal = signal[gueltig].to_numpy(dtype=float)

    if len(zeit) < 10:
        raise ValueError(
            f"In {datei.name} wurden in Spalte 4 und 5 "
            "keine ausreichenden Messdaten gefunden."
        )

    sortierung = np.argsort(zeit)
    zeit = zeit[sortierung]
    signal = signal[sortierung]

    zeit, eindeutige_indices = np.unique(
        zeit,
        return_index=True
    )
    signal = signal[eindeutige_indices]

    print(
        f"{datei.name}: Tektronix-Format erkannt, "
        f"{len(zeit)} Messpunkte geladen"
    )

    return zeit, signal


def tabellen_csv_laden(
    datei,
    trennzeichen,
    signal_suchbegriffe=()
):
    """
    Liest normale CSV-Dateien mit einer Kopfzeile ein,
    beispielsweise Exportdateien aus KiCad/ngspice.
    """
    zeilen = datei.read_text(
        encoding="utf-8-sig",
        errors="ignore"
    ).splitlines()

    kopfzeile = None

    for index, zeile in enumerate(zeilen):
        if "time" in zeile.lower() or "zeit" in zeile.lower():
            kopfzeile = index
            break

    if kopfzeile is None:
        raise ValueError(
            f"In {datei.name} wurde keine Kopfzeile "
            "mit einer Zeitspalte gefunden."
        )

    daten = pd.read_csv(
        datei,
        sep=trennzeichen,
        skiprows=kopfzeile,
        engine="python",
        on_bad_lines="skip",
        encoding_errors="ignore",
    )

    daten.columns = [
        str(spalte).strip().strip('"')
        for spalte in daten.columns
    ]

    for spalte in daten.columns:
        daten[spalte] = in_zahlen_umwandeln(
            daten[spalte],
            trennzeichen
        )

    numerische_spalten = [
        spalte
        for spalte in daten.columns
        if daten[spalte].notna().sum() >= 10
    ]

    if len(numerische_spalten) < 2:
        raise ValueError(
            f"In {datei.name} wurden nicht genug "
            "numerische Spalten gefunden."
        )

    zeitspalte = next(
        (
            spalte
            for spalte in numerische_spalten
            if "time" in spalte.lower()
            or "zeit" in spalte.lower()
        ),
        numerische_spalten[0],
    )

    signalspalten = [
        spalte
        for spalte in numerische_spalten
        if spalte != zeitspalte
    ]

    signalspalte = next(
        (
            spalte
            for spalte in signalspalten
            if any(
                suchbegriff.lower() in spalte.lower()
                for suchbegriff in signal_suchbegriffe
            )
        ),
        None,
    )

    if signalspalte is None:
        signalspalte = max(
            signalspalten,
            key=lambda spalte: daten[spalte].std(
                skipna=True
            ),
        )

    zeit = daten[zeitspalte].to_numpy(dtype=float)
    signal = daten[signalspalte].to_numpy(dtype=float)

    gueltig = np.isfinite(zeit) & np.isfinite(signal)
    zeit = zeit[gueltig]
    signal = signal[gueltig]

    sortierung = np.argsort(zeit)
    zeit = zeit[sortierung]
    signal = signal[sortierung]

    zeit, eindeutige_indices = np.unique(
        zeit,
        return_index=True
    )
    signal = signal[eindeutige_indices]

    print(
        f"{datei.name}: Zeitspalte = '{zeitspalte}', "
        f"Signalspalte = '{signalspalte}', "
        f"{len(zeit)} Punkte geladen"
    )

    return zeit, signal


def csv_signal_laden(
    datei,
    signal_suchbegriffe=(),
    tektronix=False
):
    datei = Path(datei)

    if not datei.exists():
        raise FileNotFoundError(
            f"Datei nicht gefunden: {datei}"
        )

    trennzeichen = trennzeichen_erkennen(datei)

    if tektronix:
        return tektronix_csv_laden(
            datei,
            trennzeichen
        )

    return tabellen_csv_laden(
        datei,
        trennzeichen,
        signal_suchbegriffe
    )


# ============================================================
# Gewünschte Perioden ausschneiden
# ============================================================

def letzte_perioden(
    zeit,
    signal,
    frequenz,
    anzahl_perioden
):
    dauer = anzahl_perioden / frequenz
    startzeit = zeit[-1] - dauer

    auswahl = zeit >= startzeit

    zeit_ausschnitt = zeit[auswahl]
    signal_ausschnitt = signal[auswahl]

    if len(zeit_ausschnitt) < 10:
        raise ValueError(
            "Zu wenige Datenpunkte im gewählten "
            "Periodenausschnitt."
        )

    zeit_ausschnitt = (
        zeit_ausschnitt - zeit_ausschnitt[0]
    )

    return zeit_ausschnitt, signal_ausschnitt


def normalisieren(signal):
    signal = signal - np.mean(signal)
    maximum = np.max(np.abs(signal))

    if maximum == 0:
        return signal

    return signal / maximum


# ============================================================
# Simulation und Messung vergleichen
# ============================================================

def vergleich_vorbereiten(
    sim_zeit,
    sim_signal,
    oszi_zeit,
    oszi_signal
):
    gemeinsame_dauer = min(
        sim_zeit[-1],
        oszi_zeit[-1]
    )

    gemeinsame_zeit = np.linspace(
        0,
        gemeinsame_dauer,
        2000,
        endpoint=False,
    )

    sim_roh = np.interp(
        gemeinsame_zeit,
        sim_zeit,
        sim_signal,
    )

    oszi_roh = np.interp(
        gemeinsame_zeit,
        oszi_zeit,
        oszi_signal,
    )

    sim_norm = normalisieren(sim_roh)
    oszi_norm = normalisieren(oszi_roh)

    # Simulation und Messung beginnen nicht mit derselben Phase.
    # Deshalb wird das Oszilloskopsignal automatisch verschoben.
    korrelation = np.fft.ifft(
        np.fft.fft(oszi_norm)
        * np.conj(np.fft.fft(sim_norm))
    ).real

    verschiebung = int(np.argmax(korrelation))

    oszi_roh = np.roll(
        oszi_roh,
        -verschiebung
    )

    oszi_norm = np.roll(
        oszi_norm,
        -verschiebung
    )

    return (
        gemeinsame_zeit,
        sim_roh,
        oszi_roh,
        sim_norm,
        oszi_norm,
    )


# ============================================================
# Diagramme speichern
# ============================================================

def einzelplot_speichern(
    zeit,
    signal,
    titel,
    dateiname,
    beschriftung
):
    plt.figure(figsize=(9, 4.5))

    plt.plot(
        zeit * 1e6,
        signal,
        label=beschriftung
    )

    plt.xlabel("Zeit in µs")
    plt.ylabel("Spannung in V")
    plt.title(titel)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(dateiname, dpi=200)
    plt.close()


def vergleich_speichern(
    zeit,
    sim_roh,
    oszi_roh,
    sim_norm,
    oszi_norm,
    titel,
    dateiname
):
    zeit_us = zeit * 1e6

    fig, achsen = plt.subplots(
        2,
        1,
        figsize=(9, 7),
        sharex=True,
    )

    achsen[0].plot(
        zeit_us,
        sim_roh,
        label="Simulation"
    )

    achsen[0].plot(
        zeit_us,
        oszi_roh,
        label="Oszilloskop",
        alpha=0.8,
    )

    achsen[0].set_ylabel("Spannung in V")
    achsen[0].set_title(
        f"{titel} – reale Amplituden"
    )
    achsen[0].grid(True)
    achsen[0].legend()

    achsen[1].plot(
        zeit_us,
        sim_norm,
        label="Simulation normiert",
    )

    achsen[1].plot(
        zeit_us,
        oszi_norm,
        label="Oszilloskop normiert",
        alpha=0.8,
    )

    achsen[1].set_xlabel("Zeit in µs")
    achsen[1].set_ylabel(
        "Normierte Amplitude"
    )
    achsen[1].set_title(
        "Vergleich der Signalform "
        "mit Phasenanpassung"
    )
    achsen[1].grid(True)
    achsen[1].legend()

    fig.tight_layout()
    fig.savefig(dateiname, dpi=200)
    plt.close(fig)



# ============================================================
# f/V-Kennlinie
# ============================================================

def kennlinie_speichern():
    """
    Stellt die gemessene Abstimmkennlinie des VCO dar.
    x-Achse: Abstimmspannung
    y-Achse: Ausgangsfrequenz
    """
    spannung_v = np.array([
        5.33,
        5.50,
        5.63,
        5.82,
        5.92,
        6.06,
        6.24,
        6.36,
        6.54,
        6.70,
        6.89,
    ])

    frequenz_mhz = np.array([
        6.00,
        5.90,
        5.83,
        5.69,
        5.61,
        5.52,
        5.42,
        5.33,
        5.21,
        5.11,
        5.01,
    ])

    # Zur Sicherheit nach steigender Spannung sortieren.
    sortierung = np.argsort(spannung_v)
    spannung_v = spannung_v[sortierung]
    frequenz_mhz = frequenz_mhz[sortierung]

    plt.figure(figsize=(8, 5))
    plt.plot(
        spannung_v,
        frequenz_mhz,
        marker="o",
        label="Messwerte",
    )

    plt.xlabel(r"Abstimmspannung $V_\mathrm{Tune}$ in V")
    plt.ylabel("Frequenz in MHz")
    plt.title("f/V-Kennlinie des VCO")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    dateiname = PLOT_DIR / "f_V_Kennlinie.png"
    plt.savefig(dateiname, dpi=200)
    plt.close()

    print(f"f/V-Kennlinie gespeichert: {dateiname}")

# ============================================================
# Hauptprogramm
# ============================================================

def main():
    for name, messung in MESSUNGEN.items():
        print(f"\n--- {name} ---")

        frequenz = messung["frequenz"]

        sim_zeit, sim_signal = csv_signal_laden(
            messung["simulation"],
            signal_suchbegriffe=(
                "v(out)",
                "vout",
                "output",
                "voltage",
                "spannung",
            ),
            tektronix=False,
        )

        oszi_zeit, oszi_signal = csv_signal_laden(
            messung["oszilloskop"],
            tektronix=True,
        )

        sim_zeit, sim_signal = letzte_perioden(
            sim_zeit,
            sim_signal,
            frequenz,
            N_PERIODS,
        )

        oszi_zeit, oszi_signal = letzte_perioden(
            oszi_zeit,
            oszi_signal,
            frequenz,
            N_PERIODS,
        )

        dateiname = (
            name.replace(" ", "_")
            .replace(",", "_")
        )

        einzelplot_speichern(
            sim_zeit,
            sim_signal,
            (
                f"Simulation bei {name} – "
                f"letzte {N_PERIODS} Perioden"
            ),
            PLOT_DIR
            / f"simulation_{dateiname}.png",
            "Simulation",
        )

        einzelplot_speichern(
            oszi_zeit,
            oszi_signal,
            (
                f"Oszilloskop bei {name} – "
                f"letzte {N_PERIODS} Perioden"
            ),
            PLOT_DIR
            / f"oszilloskop_{dateiname}.png",
            "Oszilloskop",
        )

        (
            gemeinsame_zeit,
            sim_roh,
            oszi_roh,
            sim_norm,
            oszi_norm,
        ) = vergleich_vorbereiten(
            sim_zeit,
            sim_signal,
            oszi_zeit,
            oszi_signal,
        )

        vergleich_speichern(
            gemeinsame_zeit,
            sim_roh,
            oszi_roh,
            sim_norm,
            oszi_norm,
            f"Simulation und Messung bei {name}",
            PLOT_DIR
            / f"vergleich_{dateiname}.png",
        )

    kennlinie_speichern()

    print(
        "\nFertig. Diagramme gespeichert unter:"
        f"\n{PLOT_DIR}"
    )


if __name__ == "__main__":
    main()