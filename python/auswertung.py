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

N_PERIODS = 2

# Sichtbarer Bereich der direkt berechneten FFT.
# Die FFT selbst wird weiterhin aus der vollständigen CSV berechnet.
FFT_MIN_MHZ = 0
FFT_MAX_MHZ = 30

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



def perioden_phasengleich(
    zeit,
    signal,
    frequenz,
    anzahl_perioden,
    anzahl_ausgabepunkte=2000
):
    """
    Schneidet einen eingeschwungenen Ausschnitt aus und setzt
    t = 0 auf einen steigenden Nulldurchgang bezogen auf den
    Mittelwert des Signals.

    Dadurch starten verschiedene Frequenzen im gemeinsamen Plot
    mit derselben Phase.
    """
    dauer = anzahl_perioden / frequenz
    signal_zentriert = signal - np.mean(signal)

    # Steigende Durchgänge durch den Mittelwert suchen.
    kandidaten = np.where(
        (signal_zentriert[:-1] <= 0)
        & (signal_zentriert[1:] > 0)
    )[0]

    startzeiten = []

    for index in kandidaten:
        y1 = signal_zentriert[index]
        y2 = signal_zentriert[index + 1]
        t1 = zeit[index]
        t2 = zeit[index + 1]

        if y2 == y1:
            startzeit = t1
        else:
            anteil = -y1 / (y2 - y1)
            startzeit = t1 + anteil * (t2 - t1)

        if startzeit + dauer <= zeit[-1]:
            startzeiten.append(startzeit)

    if startzeiten:
        # Letzten möglichen Durchgang verwenden:
        # Simulation liegt dadurch sicher im eingeschwungenen Zustand.
        startzeit = startzeiten[-1]
    else:
        # Fallback, falls kein vollständiger Durchgang gefunden wird.
        startzeit = max(
            zeit[0],
            zeit[-1] - dauer
        )

    relative_zeit = np.linspace(
        0,
        dauer,
        anzahl_ausgabepunkte,
        endpoint=False,
    )

    signal_ausschnitt = np.interp(
        startzeit + relative_zeit,
        zeit,
        signal,
    )

    return relative_zeit, signal_ausschnitt


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
    """
    Bereitet Simulation und Messung für den direkten Vergleich vor.

    Beide Ausschnitte beginnen bereits bei einem steigenden
    Durchgang durch den jeweiligen Mittelwert. Hier werden sie
    nur noch auf dasselbe Zeitraster gebracht, zentriert und
    auf dieselbe Amplitude normiert.
    """
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

    sim_interp = np.interp(
        gemeinsame_zeit,
        sim_zeit,
        sim_signal,
    )

    oszi_interp = np.interp(
        gemeinsame_zeit,
        oszi_zeit,
        oszi_signal,
    )

    sim_norm = normalisieren(sim_interp)
    oszi_norm = normalisieren(oszi_interp)

    return gemeinsame_zeit, sim_norm, oszi_norm


# ============================================================
# Diagramme speichern
# ============================================================

def mehrere_verlaeufe_speichern(
    signale,
    titel,
    dateiname
):
    """
    Zeichnet mehrere Zeitverläufe gemeinsam in ein Diagramm.

    signale ist ein Dictionary mit:
        Bezeichnung: (Zeitarray, Signalarrray)
    """
    plt.figure(figsize=(9, 5))

    for bezeichnung, (zeit, signal) in signale.items():
        plt.plot(
            zeit * 1e6,
            signal,
            label=bezeichnung,
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
    sim_signal,
    oszi_signal,
    titel,
    dateiname
):
    """
    Zeichnet nur den normierten, phasengleichen Vergleich.
    """
    plt.figure(figsize=(9, 5))

    plt.plot(
        zeit * 1e6,
        sim_signal,
        label="Simulation",
    )

    plt.plot(
        zeit * 1e6,
        oszi_signal,
        label="Oszilloskop",
        alpha=0.8,
    )

    plt.xlabel("Zeit in µs")
    plt.ylabel("Normierte Amplitude")
    plt.title(titel)
    plt.ylim(-1.1, 1.1)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(dateiname, dpi=200)
    plt.close()


# ============================================================
# FFT der vollständigen Oszilloskopaufnahme
# ============================================================

def fft_oszilloskop_speichern(
    zeit,
    signal,
    titel,
    mittenfrequenz_hz,
    dateiname
):
    """
    Direkte FFT der vollständigen Oszilloskopaufnahme:
    - kein Fenster
    - kein Zero-Padding
    - keine Filterung
    - keine dB-Normierung
    """
    if len(zeit) < 2:
        raise ValueError(
            "Für die FFT sind zu wenige Messpunkte vorhanden."
        )

    dt = np.mean(np.diff(zeit))

    if dt <= 0:
        raise ValueError(
            "Der Zeitabstand der Oszilloskopdaten ist ungültig."
        )

    anzahl_punkte = len(signal)

    fft_werte = np.fft.rfft(signal)
    frequenzen = np.fft.rfftfreq(
        anzahl_punkte,
        d=dt,
    )

    # Einseitiges Amplitudenspektrum in Volt.
    amplituden = np.abs(fft_werte) / anzahl_punkte

    if anzahl_punkte > 1:
        amplituden[1:-1] *= 2.0

    plt.figure(figsize=(9, 5))
    plt.stem(
        frequenzen / 1e6,
        amplituden,
        linefmt="C0-",
        markerfmt="C0o",
        basefmt=" ",
        label="FFT",
    )

    plt.xlabel("Frequenz in MHz")
    plt.ylabel("Amplitude in V")
    plt.title(
        f"FFT der Oszilloskopaufnahme bei {titel}"
    )
    plt.xlim(
        FFT_MIN_MHZ,
        FFT_MAX_MHZ,
    )
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(dateiname, dpi=200)
    plt.close()

    frequenzabstand = frequenzen[1] - frequenzen[0]

    print(
        f"FFT {titel}: Frequenzabstand "
        f"{frequenzabstand / 1e6:.3f} MHz"
    )


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
    simulationsverlaeufe = {}
    oszilloskopverlaeufe = {}

    # Veraltete Vergleichsplots entfernen.
    for alter_plot in PLOT_DIR.glob("vergleich_*.png"):
        alter_plot.unlink()

    for name, messung in MESSUNGEN.items():
        print(f"\n--- {name} ---")

        frequenz = messung["frequenz"]

        sim_zeit_gesamt, sim_signal_gesamt = csv_signal_laden(
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

        oszi_zeit_gesamt, oszi_signal_gesamt = csv_signal_laden(
            messung["oszilloskop"],
            tektronix=True,
        )

        dateiname = (
            name.replace(" ", "_")
            .replace(",", "_")
        )

        # FFT weiterhin aus der vollständigen Oszilloskopaufnahme.
        fft_oszilloskop_speichern(
            oszi_zeit_gesamt,
            oszi_signal_gesamt,
            name,
            frequenz,
            PLOT_DIR / f"fft_{dateiname}.png",
        )

        # Für die gemeinsamen Zeitplots beginnen alle Signale
        # bei einem steigenden Durchgang durch ihren Mittelwert.
        sim_zeit, sim_signal = perioden_phasengleich(
            sim_zeit_gesamt,
            sim_signal_gesamt,
            frequenz,
            N_PERIODS,
        )

        oszi_zeit, oszi_signal = perioden_phasengleich(
            oszi_zeit_gesamt,
            oszi_signal_gesamt,
            frequenz,
            N_PERIODS,
        )

        simulationsverlaeufe[name] = (
            sim_zeit,
            sim_signal,
        )

        oszilloskopverlaeufe[name] = (
            oszi_zeit,
            oszi_signal,
        )

        (
            gemeinsame_zeit,
            sim_norm,
            oszi_norm,
        ) = vergleich_vorbereiten(
            sim_zeit,
            sim_signal,
            oszi_zeit,
            oszi_signal,
        )

        # Vergleich nur mit zentrierten und normierten Signalen,
        # damit beide Schwingungen wirklich übereinander liegen.
        vergleich_speichern(
            gemeinsame_zeit,
            sim_norm,
            oszi_norm,
            (
                f"Simulation und Oszilloskop bei {name} "
                f"– normiert und phasengleich, {N_PERIODS} Perioden"
            ),
            PLOT_DIR / f"vergleich_{dateiname}.png",
        )

    # Alle drei Simulationsverläufe gemeinsam.
    mehrere_verlaeufe_speichern(
        simulationsverlaeufe,
        (
            "Simulierte VCO-Signale "
            f"– phasengleich, {N_PERIODS} Perioden"
        ),
        PLOT_DIR / "simulation_alle_frequenzen.png",
    )

    # Alle drei Oszilloskopverläufe gemeinsam.
    mehrere_verlaeufe_speichern(
        oszilloskopverlaeufe,
        (
            "Gemessene VCO-Signale "
            f"– phasengleich, {N_PERIODS} Perioden"
        ),
        PLOT_DIR / "oszilloskop_alle_frequenzen.png",
    )

    kennlinie_speichern()

    print(
        "\nFertig. Diagramme gespeichert unter:"
        f"\n{PLOT_DIR}"
    )


if __name__ == "__main__":
    main()