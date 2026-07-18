# FM-VCO

Dieses Repository enthält die Entwicklung, Simulation und praktische Umsetzung eines spannungsgesteuerten Oszillators für einen Frequenzmodulator.

Der VCO wird in **KiCad** aufgebaut und mit **ngspice** simuliert. Anschließend soll die Schaltung auf einer Platine umgesetzt und messtechnisch untersucht werden.

## Anforderungen

Für den Frequenzmodulator wurden folgende Anforderungen vorgegeben:

- Mittenfrequenz von **5,5 MHz**
- einstellbarer Frequenzbereich um die Mittenfrequenz
- nutzbarer Frequenzbereich von **5 MHz bis 6 MHz**
- Eingangssignal im Bereich von ungefähr **±0,5 V**
- möglichst linearer Zusammenhang zwischen Eingangsspannung und Ausgangsfrequenz
- möglichst geringe nichtlineare Abweichungen
- ausreichend große Bandbreite für den Einsatz als Frequenzmodulator
- ein Eingang und ein Ausgang über BNC-Buchsen
- Ein- und Ausgang sollen auf **50 Ω** angepasst sein
- Frequenzdrift soll durch eine Gleichspannung korrigierbar sein
- robuste Platine für einen stabilen und übersichtlichen Aufbau
- Kennlinie soll mithilfe einer Gleichspannung aufgenommen werden können
- Ausgangsspannung soll messbar sein
- Schaltung soll möglichst kurzschlusssicher sein

## Grundlagen und Aufbau des VCOs

### Vom Schwingkreis zum Oszillator

Die Grundlage des VCOs bildet ein LC-Schwingkreis aus Induktivitäten und Kapazitäten. Im Schwingkreis wird Energie periodisch zwischen dem magnetischen Feld der Induktivitäten und dem elektrischen Feld der Kapazitäten ausgetauscht.

Die Resonanzfrequenz kann näherungsweise mit

$$
f_0 \approx \frac{1}{2\pi\sqrt{L_\text{eff}C_\text{eff}}}
$$

beschrieben werden.

Dabei sind:

- $L_\text{eff}$ die wirksame Induktivität des Schwingkreises
- $C_\text{eff}$ die gesamte wirksame Kapazität einschließlich parasitärer Kapazitäten

Ein realer LC-Schwingkreis besitzt Verluste, beispielsweise durch die Innenwiderstände der Induktivitäten, Leiterbahnen und angeschlossene Messgeräte. Ohne zusätzliche Energiezufuhr würde die Schwingung deshalb mit der Zeit abklingen.

Damit eine dauerhafte Schwingung entsteht, muss eine aktive Schaltung die Verluste des Schwingkreises ausgleichen. Dazu wird ein Teil des Ausgangssignals phasenrichtig zurückgeführt und verstärkt. Beim Einschalten reichen bereits kleine Störungen und das elektrische Rauschen aus, um eine Schwingung anzuregen. Die Frequenzanteile in der Nähe der Resonanzfrequenz werden anschließend durch die Rückkopplung verstärkt.

Für das Anschwingen muss die Schleifenverstärkung zunächst ausreichend groß sein. Im eingeschwungenen Zustand stellt sich die Amplitude so ein, dass die zugeführte Energie den Verlusten des Schwingkreises entspricht.

### Aufbau des VCOs

Der verwendete VCO besteht grundsätzlich aus einem differentiellen LC-Schwingkreis, einem gekreuzt gekoppelten MOSFET-Paar und einer Stromquelle.

<p align="center">
  <img
    src="images/vco-grundaufbau.png"
    alt="Grundaufbau eines differentiellen LC-VCOs mit Cross-Coupled-MOSFETs"
    width="650">
</p>

<p align="center">
  <em>
    Vereinfachter Aufbau eines differentiellen LC-VCOs.
    Quelle:
    <a href="https://analogcircuitdesign.com/voltage-controlled-oscillator/">
      Analog Circuit Design
    </a>
  </em>
</p>

Der VCO setzt sich aus folgenden Funktionsgruppen zusammen:

| Funktionsgruppe | Bauteile der aktuellen Schaltung | Aufgabe |
|---|---|---|
| LC-Schwingkreis | `L1`, `L2`, `D1`, `D2` | Festlegung der Resonanzfrequenz |
| Cross-Coupled-Paar | `Q1`, `Q2` | Ausgleich der Schwingkreisverluste |
| Frequenzabstimmung | `D1`, `D2`, `Vtune` | Veränderung der wirksamen Kapazität |
| Stromquelle | `Q3`, `Q4`, `R4` | Einstellung und Begrenzung des Arbeitspunktstroms |
| Ausgang | rechter Schwingkreisknoten | Ausgabe des hochfrequenten Signals |

Die beiden MOSFETs `Q1` und `Q2` sind über Kreuz miteinander gekoppelt. Das Gate jedes Transistors ist mit dem Drain des jeweils anderen Transistors verbunden.

Durch diese Rückkopplung erzeugt das Transistorpaar einen negativen differentiellen Widerstand. Dieser wirkt den realen Verlusten des LC-Schwingkreises entgegen und ermöglicht eine dauerhafte Schwingung.

Die beiden Schwingkreisknoten schwingen näherungsweise gegenphasig. Steigt die Spannung an einem Knoten an, fällt sie am anderen Knoten ab. Das vollständige differentielle Ausgangssignal ergibt sich aus der Spannungsdifferenz zwischen beiden Knoten:

$$
u_\text{diff}(t)=u_1(t)-u_2(t)
$$

In der aktuellen Schaltung wird das Ausgangssignal nur an einem der beiden Schwingkreisknoten gegen Masse abgegriffen. Der herausgeführte Ausgang ist damit Single-Ended, obwohl der Oszillator intern differentiell arbeitet.

Die Resonanzfrequenz des Schwingkreises kann näherungsweise mit folgender Gleichung beschrieben werden:

$$
f_0 \approx \frac{1}{2\pi\sqrt{L_\text{eff}C_\text{eff}}}
$$

Dabei sind:

- $L_\text{eff}$ die wirksame Induktivität
- $C_\text{eff}$ die wirksame Kapazität einschließlich parasitärer Kapazitäten

Die Kapazität der Varaktordioden `D1` und `D2` wird über die Abstimmspannung `Vtune` verändert. Dadurch verändert sich die Resonanzfrequenz und somit die Ausgangsfrequenz des Oszillators.

Für die Stromversorgung des Cross-Coupled-Paares wird ein einfacher NMOS-Stromspiegel eingesetzt. Dieser besteht aus den Transistoren `Q3` und `Q4` sowie dem Widerstand `R4`.

### Cross-Coupled-Transistorpaar

Die MOSFETs `Q1` und `Q2` sind über Kreuz miteinander gekoppelt. Das Gate eines Transistors ist jeweils mit dem Drain des anderen Transistors verbunden.

Die beiden Schwingkreisknoten schwingen dadurch näherungsweise gegenphasig. Steigt die Spannung an einem Knoten an, fällt sie am anderen Knoten ab.

Das Transistorpaar erzeugt im Schwingkreis einen negativen differentiellen Widerstand. Dieser wirkt den realen Verlustwiderständen des Schwingkreises entgegen. Sind die Verluste ausreichend kompensiert, kann die Schwingung dauerhaft bestehen bleiben.

Die Schaltung arbeitet intern differenziell. Das bedeutet, dass das vollständige Signal als Spannungsdifferenz zwischen den beiden Schwingkreisknoten betrachtet werden kann:

$$
u_\text{diff}(t)=u_1(t)-u_2(t)
$$

Wird nur einer der beiden Knoten gegen Masse gemessen, handelt es sich dagegen um einen unsymmetrischen beziehungsweise Single-Ended-Ausgang.

### Spannungsabhängige Frequenzabstimmung

Damit aus dem LC-Oszillator ein spannungsgesteuerter Oszillator wird, werden die festen Kapazitäten teilweise durch Varaktordioden ersetzt.

Eine Varaktordiode wird in Sperrrichtung betrieben und verhält sich dabei näherungsweise wie ein spannungsabhängiger Kondensator. Die Abstimmspannung `Vtune` verändert die Sperrspannung und damit die Kapazität der Dioden.

Dadurch verändert sich die wirksame Kapazität des Schwingkreises:

$$
V_\text{tune}
\longrightarrow
C_\text{Varaktor}
\longrightarrow
f_\text{out}
$$

In der aktuellen Schaltung nimmt die gemessene Ausgangsfrequenz mit zunehmender Spannung `Vtune` ab. Die genaue Richtung der Frequenzänderung hängt von der Verschaltung der Varaktordioden und den Spannungsverhältnissen innerhalb des Schwingkreises ab.

Für einen möglichst verzerrungsarmen Frequenzmodulator sollte der Zusammenhang zwischen Abstimmspannung und Ausgangsfrequenz im verwendeten Arbeitsbereich möglichst linear sein:

$$
f_\text{out}
\approx
f_\text{Mitte}
+
K_\text{VCO}\cdot\left(V_\text{tune}-V_\text{Mitte}\right)
$$

Dabei beschreibt $K_\text{VCO}$ die Empfindlichkeit des VCOs und wird beispielsweise in `MHz/V` angegeben.

### NMOS-Stromspiegel

Die Stromquelle des VCOs wird als einfacher NMOS-Stromspiegel ausgeführt.

<p align="center">
  <img
    src="images/nmos-stromspiegel.png"
    alt="Einfacher NMOS-Stromspiegel mit Referenzwiderstand"
    width="550">
</p>

<p align="center">
  <em>
    Prinzip eines einfachen NMOS-Stromspiegels.
    Quelle:
    <a href="https://www.allaboutcircuits.com/technical-articles/the-basic-mosfet-constant-current-source/">
      All About Circuits
    </a>
  </em>
</p>

Der Stromspiegel besteht in der aktuellen Schaltung aus den MOSFETs `Q3` und `Q4` sowie dem Widerstand `R4`.

Bei `Q4` sind Gate und Drain miteinander verbunden. Der Transistor ist damit als Referenztransistor beschaltet. Über den Widerstand `R4` stellt sich ein Referenzstrom ein.

Da die Gates von `Q3` und `Q4` miteinander verbunden sind, liegt an beiden MOSFETs näherungsweise dieselbe Gate-Source-Spannung an. Dadurch übernimmt `Q3` näherungsweise den Strom des Referenzzweigs und stellt den Arbeitspunktstrom für das Cross-Coupled-Transistorpaar bereit.

Die Bauteile der Prinzipschaltung entsprechen in der aktuellen VCO-Schaltung folgenden Bauteilen:

| Prinzipschaltung | Aktuelle Schaltung |
|---|---|
| Referenztransistor `Q1` | `Q4` |
| Ausgangstransistor `Q2` | `Q3` |
| Einstellwiderstand `RSET` | `R4` |
| Referenzstrom `IREF` | Strom durch `R4` und `Q4` |
| Ausgangsstrom `IBIAS` | Arbeitspunktstrom für `Q1` und `Q2` |

Der Stromspiegel übernimmt unter anderem folgende Aufgaben:

- Einstellung des Arbeitspunktstroms
- Begrenzung des Stroms durch den Oszillator
- Unterstützung eines zuverlässigen Anschwingens
- Verringerung großer Stromschwankungen
- Beeinflussung der Ausgangsamplitude
- Schutz der MOSFETs vor zu hohen Strömen

Der Referenzstrom kann vereinfacht mit folgender Gleichung abgeschätzt werden:

$$
I_\text{REF}
\approx
\frac{V_\text{DD}-V_\text{GS}}{R_4}
$$

Diese Gleichung ist nur eine Näherung, da die Gate-Source-Spannung `VGS` vom verwendeten MOSFET, vom Strom und von der Temperatur abhängt.

Im realen Aufbau wird für `R4` ein Widerstand von **51 kΩ** verwendet. Bei einem deutlich größeren Widerstand ist der Strom zu klein, sodass der Oszillator nicht zuverlässig zu schwingen beginnt.

In der SPICE-Simulation wird dagegen ein deutlich größerer Widerstand verwendet. Bei einem Widerstand von **51 kΩ** treten in der Simulation stärkere Verzerrungen des Ausgangssignals auf.

Dieser Unterschied zeigt, dass das verwendete MOSFET-Modell das reale Verhalten des Stromspiegels nur näherungsweise abbildet.

Der einfache NMOS-Stromspiegel ist keine ideale Stromquelle. Der erzeugte Strom wird unter anderem durch folgende Eigenschaften beeinflusst:

- Bauteiltoleranzen der MOSFETs
- unterschiedliche Gate-Source-Schwellspannungen
- Drain-Source-Spannung von `Q3`
- Temperatur
- Versorgungsspannung
- Ausgangswiderstand der MOSFETs

Der Stromspiegel stabilisiert damit den Arbeitspunkt der Schaltung, stellt jedoch keine vollständige automatische Regelung der Ausgangsamplitude dar.

### Einsatz als Frequenzmodulator

Für die Frequenzmodulation wird der Abstimmspannung eine Gleichspannung und ein zeitlich veränderliches Modulationssignal überlagert:

$$
V_\text{tune}(t)
=
V_\text{DC}
+
v_\text{mod}(t)
$$

Die Gleichspannung $V_\text{DC}$ legt die Mittenfrequenz fest. Das Modulationssignal $v_\text{mod}(t)$ verändert die Momentanfrequenz um diese Mittenfrequenz.

Bei einer annähernd linearen VCO-Kennlinie gilt näherungsweise:

$$
f_\text{out}(t)
=
f_\text{Mitte}
+
K_\text{VCO}\cdot v_\text{mod}(t)
$$

Die Amplitude des Modulationssignals bestimmt damit den Frequenzhub. Die Frequenz des Modulationssignals bestimmt, wie schnell die Ausgangsfrequenz zwischen ihren Grenzwerten verändert wird.

Damit die Frequenzmodulation möglichst unverzerrt erfolgt, muss das Modulationssignal innerhalb des annähernd linearen Bereichs der aufgenommenen VCO-Kennlinie bleiben.

## Verwendete Bauteile

Für den aktuellen Aufbau werden unter anderem folgende Bauteile verwendet:

| Bezeichnung | Bauteil | Funktion | Datenblatt |
|---|---|---|---|
| Q1, Q2 | [`BS170`](https://www.onsemi.com/download/data-sheet/pdf/mmbf170-d.pdf) | Cross-Coupled-Transistorpaar | [![BS170-Datenblatt](https://img.shields.io/badge/BS170-Datenblatt%20öffnen-blue?style=for-the-badge)](https://www.onsemi.com/download/data-sheet/pdf/mmbf170-d.pdf) |
| Q3, Q4 | [`BS170`](https://www.onsemi.com/download/data-sheet/pdf/mmbf170-d.pdf) | NMOS-Stromspiegel | [![BS170-Datenblatt](https://img.shields.io/badge/BS170-Datenblatt%20öffnen-blue?style=for-the-badge)](https://www.onsemi.com/download/data-sheet/pdf/mmbf170-d.pdf) |
| D1, D2 | [`1SV149`](https://www.radiomuseum.co.uk/filter/1SV149.pdf) | Varaktordioden zur Frequenzabstimmung | [![1SV149-Datenblatt](https://img.shields.io/badge/1SV149-Datenblatt%20öffnen-green?style=for-the-badge)](https://www.radiomuseum.co.uk/filter/1SV149.pdf) |
| L1, L2 | 3,3 µH | Induktiver Teil des Schwingkreises | – |
| R4 | 51 kΩ | Einstellung des Referenzstroms im realen Aufbau | – |

Die Bauteilwerte können sich während der weiteren Entwicklung und Optimierung noch ändern.

## Simulation

Die Simulation der Schaltung wird in KiCad mit ngspice durchgeführt.

Untersucht werden unter anderem:

- Startverhalten des Oszillators
- Ausgangsfrequenz
- Ausgangsamplitude
- Frequenzänderung in Abhängigkeit von `Vtune`
- Stromaufnahme
- Arbeitspunkt der MOSFETs
- Verhalten der Stromquelle
- Linearität der Frequenzkennlinie
- Einfluss der Bauteilwerte
- Einfluss der Belastung am Ausgang

Für die Bestimmung der Ausgangsfrequenz wird eine Transientenanalyse durchgeführt. Aus dem zeitlichen Ausgangssignal kann anschließend die Periodendauer oder das Frequenzspektrum bestimmt werden.

## Abweichungen zwischen Simulation und realem Aufbau

Die SPICE-Simulation bildet das Verhalten der realen Schaltung nur näherungsweise ab.

Mögliche Ursachen für Abweichungen sind:

- vereinfachtes SPICE-Modell der Varaktordioden
- Abweichungen der MOSFET-Modelle vom realen Verhalten
- Bauteiltoleranzen
- parasitäre Kapazitäten und Induktivitäten
- Innenwiderstände der Induktivitäten
- Leiterbahnen und Steckverbindungen
- Belastung durch Tastköpfe und Messgeräte
- Temperaturabhängigkeit der Bauteile
- Störungen und Schwankungen der Versorgungsspannung

Für den NMOS-Stromspiegel werden in der Simulation und im realen Aufbau unterschiedliche Widerstandswerte verwendet. Im realen Aufbau wird ein Widerstand von **51 kΩ** eingesetzt. Bei einem größeren Widerstand ist der Strom zu gering, sodass der Oszillator nicht zuverlässig zu schwingen beginnt. In der SPICE-Simulation wird dagegen ein größerer Widerstand benötigt, da kleinere Widerstandswerte zu Verzerrungen des Ausgangssignals führen.

Im realen Aufbau wurden außerdem Kondensatoren parallel zur Spannungsversorgung geschaltet. Diese dienen als Abblock- beziehungsweise Stützkondensatoren und reduzieren hochfrequente Störungen sowie kurzzeitige Spannungsschwankungen. Dadurch wird die Versorgungsspannung direkt an der Schaltung stabilisiert und das Schwingverhalten des VCOs verbessert.

Die Kondensatoren sollten auf der späteren Platine möglichst nah an den Versorgungspins der MOSFETs angeordnet werden.

## Aktueller Stand

Der VCO wurde sowohl in SPICE simuliert als auch praktisch aufgebaut. Über die Abstimmspannung `Vtune` lässt sich die Ausgangsfrequenz nahezu linear einstellen.

Der bisher erreichte Frequenzbereich liegt zwischen ungefähr **5,01 MHz und 6,00 MHz**. Dafür wird `Vtune` zwischen ungefähr **5,33 V und 6,89 V** verändert. Die Mittenfrequenz von etwa **5,5 MHz** wird ebenfalls erreicht.

Die Ausgangsamplitude bleibt über einen großen Teil des Frequenzbereichs relativ stabil, nimmt jedoch in Richtung **6 MHz** ab.

Für den NMOS-Stromspiegel wird im realen Aufbau ein Widerstand von **51 kΩ** verwendet. In der SPICE-Simulation ist ein deutlich größerer Widerstand notwendig, da es bei kleineren Widerstandswerten zu Verzerrungen des simulierten Ausgangssignals kommt.

Eine erste Platine wurde bereits in KiCad erstellt. Das Layout muss jedoch noch an den aktuellen Schaltungsstand angepasst und weiter optimiert werden.

## Noch nicht vollständig erfüllte Anforderungen

Folgende Anforderungen müssen noch untersucht beziehungsweise umgesetzt werden:

- Anpassung des Abstimmeingangs an das vorgegebene Eingangssignal von ungefähr **±0,5 V**
- genauere Bestimmung der nichtlinearen Abweichungen der Frequenzkennlinie
- Untersuchung der Bandbreite des Modulationseingangs
- Stabilisierung der Ausgangsamplitude in Richtung **6 MHz**
- Einkopplung des Modulationssignals zusammen mit einer einstellbaren Gleichspannung
- Anpassung des Eingangs auf **50 Ω**
- Anpassung des Ausgangs auf **50 Ω**
- Ergänzung einer Ausgangspufferung zur Entkopplung des Schwingkreises
- kurzschlusssichere Auslegung des Ausgangs
- Untersuchung der Frequenzdrift und der Temperaturabhängigkeit
- Anpassung und Optimierung des bereits erstellten Platinenlayouts
- Aufbau und Prüfung der endgültigen Platine
- Umsetzung von jeweils einem Ein- und Ausgang über BNC-Buchsen
- Prüfung der Schaltung unter realer 50-Ω-Belastung

## Ausführliche Dokumentation

Eine ausführliche Darstellung des Entwicklungsstands befindet sich in einem separaten Quarto-Bericht innerhalb dieses Repositorys.

Der Bericht enthält unter anderem:

- die vollständige Kennlinie zwischen `Vtune` und Ausgangsfrequenz
- grafische Auswertung der Messwerte
- simulierte Ausgangssignale
- am Oszilloskop aufgenommene Ausgangssignale
- Vergleich zwischen Simulation und realem Aufbau
- Untersuchung der Ausgangsamplitude
- Beschreibung der Unterschiede zwischen den Bauteilwerten in der Simulation und im realen Aufbau

## Verwendete Software

Für die Entwicklung, Simulation und Versionsverwaltung werden folgende Programme verwendet:

| Software | Verwendung | Download |
|---|---|---|
| KiCad | Erstellung des Schaltplans und des Platinenlayouts | [![KiCad herunterladen](https://img.shields.io/badge/KiCad-herunterladen-blue?style=for-the-badge&logo=kicad)](https://www.kicad.org/download/) |
| ngspice | Simulation der Schaltung und Untersuchung des VCO-Verhaltens | [![ngspice herunterladen](https://img.shields.io/badge/ngspice-herunterladen-green?style=for-the-badge)](https://ngspice.sourceforge.io/download.html) |
| Git | Lokale Versionsverwaltung des Projekts | [![Git herunterladen](https://img.shields.io/badge/Git-herunterladen-orange?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/install/) |
| GitHub | Speicherung und gemeinsame Bearbeitung des Repositorys | [![GitHub öffnen](https://img.shields.io/badge/GitHub-öffnen-black?style=for-the-badge&logo=github)](https://github.com/) |

KiCad verwendet für die integrierte SPICE-Simulation ngspice. Abhängig von der KiCad-Installation kann ngspice daher bereits enthalten sein.

## Projekt öffnen

Das Repository kann mit folgendem Befehl geklont werden:

```bash
git clone <URL-DES-REPOSITORY>
```

Der aktuelle Stand des KiCad-Projekts befindet sich im folgenden Unterordner:

```text
kicad/FM-ELK_LC-VCO-FINAL
```

Anschließend kann die darin enthaltene `.kicad_pro`-Datei mit KiCad geöffnet werden.

Vor der Simulation sollte überprüft werden, ob:

- alle Symbolbibliotheken vorhanden sind
- alle Footprints korrekt zugeordnet sind
- das SPICE-Modell der `1SV149` eingebunden ist
- die Modellpfade in KiCad korrekt eingestellt sind

## Mitwirkende

<p>
  <a href="https://github.com/madraeger">
    <img src="https://img.shields.io/badge/GitHub-Maurice%20Draeger-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub-Profil von Maurice Draeger">
  </a>
  <a href="https://github.com/ethaniellingkoenig">
    <img src="https://img.shields.io/badge/GitHub-Ethaniel%20Ingkoenig-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub-Profil von Ethaniel Ingkoenig">
  </a>
</p>

## Literaturverzeichnis

Die folgenden Quellen wurden für die Grundlagen und die Entwicklung der Schaltung verwendet:

1. [Analog Circuit Design: Voltage Controlled Oscillator – VCO Basics, Operation, Tuning and Use in Communication Circuits](https://analogcircuitdesign.com/voltage-controlled-oscillator/)  
   Grundlagen zu spannungsgesteuerten Oszillatoren, LC-VCOs, Varaktordioden und VCO-Kennlinien.

2. [Electronics Tutorials: LC Oscillator Tutorial and Tuned LC Oscillator Basics](https://www.electronics-tutorials.ws/oscillator/oscillators.html)  
   Grundlagen zu LC-Schwingkreisen, Rückkopplung und den Bedingungen für eine dauerhafte Schwingung.

3. [ElektronikTutor: Frequenzmodulation](https://www.elektroniktutor.de/signalkunde/fm.html)  
   Grundlagen zur Frequenzmodulation, zum Frequenzhub, zum Modulationsindex und zur Bandbreite eines FM-Signals.

4. [All About Circuits: The Basic MOSFET Constant-Current Source](https://www.allaboutcircuits.com/technical-articles/the-basic-mosfet-constant-current-source/)  
   Grundlagen zur MOSFET-Stromquelle und zum Stromspiegel.

Alle Internetquellen wurden zuletzt am **18. Juli 2026** abgerufen.