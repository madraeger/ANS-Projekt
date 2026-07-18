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

Der LC-Schwingkreis bestimmt die Ausgangsfrequenz. Das Cross-Coupled-Transistorpaar führt dem Schwingkreis die durch reale Verluste abgegebene Energie wieder zu. Die Varaktordioden ermöglichen die spannungsabhängige Frequenzeinstellung über `Vtune`.

Als Stromquelle wird ein einfacher NMOS-Stromspiegel verwendet. Dieser stellt den Arbeitspunktstrom für das Cross-Coupled-Transistorpaar bereit.

Die einzelnen Funktionsgruppen werden in den folgenden Abschnitten genauer beschrieben.
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
V_\text{tune}(t) = V_\text{DC} + v_\text{mod}(t)
$$

Die Gleichspannung $V_\text{DC}$ legt die Mittenfrequenz fest. Das Modulationssignal $v_\text{mod}(t)$ verändert die Momentanfrequenz um diese Mittenfrequenz.

Bei einer annähernd linearen VCO-Kennlinie gilt näherungsweise:

$$
f_\text{out}(t) = f_\text{Mitte} + K_\text{VCO}\cdot v_\text{mod}(t)
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

Der VCO wurde sowohl in **SPICE simuliert** als auch **praktisch aufgebaut**. Der geforderte nutzbare Frequenzbereich von ungefähr **5 MHz bis 6 MHz** wird bereits erreicht.

Die Ausgangsfrequenz wird über die Abstimmspannung `Vtune` eingestellt. Mit steigender Abstimmspannung sinkt die Ausgangsfrequenz. Die aufgenommenen Messwerte zeigen dabei einen nahezu linearen Zusammenhang zwischen `Vtune` und der Ausgangsfrequenz.

### Gemessene f/V-Kennlinie

Die Kennlinie wurde aufgenommen, indem die Gleichspannung `Vtune` schrittweise verändert und die jeweilige Ausgangsfrequenz gemessen wurde.

| `Vtune` in V | Frequenz in MHz |
|---:|---:|
| 5,33 | 6,00 |
| 5,50 | 5,90 |
| 5,63 | 5,83 |
| 5,82 | 5,69 |
| 5,92 | 5,61 |
| 6,06 | 5,52 |
| 6,24 | 5,42 |
| 6,36 | 5,33 |
| 6,54 | 5,21 |
| 6,70 | 5,11 |
| 6,89 | 5,01 |

<p align="center">
  <img
    src="python/plots/f_V_Kennlinie.png"
    alt="Gemessene f/V-Kennlinie des VCOs"
    width="850">
</p>

<p align="center">
  <em>Gemessene Ausgangsfrequenz in Abhängigkeit von der Abstimmspannung Vtune</em>
</p>

Die Kennlinie lässt sich im betrachteten Bereich näherungsweise durch folgende lineare Funktion beschreiben:

$$
f_\text{out}
\approx
-0{,}650\,
\frac{\text{MHz}}{\text{V}}
\cdot V_\text{tune}
+
9{,}468\,\text{MHz}
$$

Das Bestimmtheitsmaß der linearen Näherung beträgt ungefähr:

$$
R^2 \approx 0{,}9989
$$

Damit zeigt die aufgenommene Kennlinie nur geringe Abweichungen von einem linearen Verlauf.

Die VCO-Empfindlichkeit beträgt näherungsweise:

$$
K_\text{VCO}
\approx
-0{,}650\,
\frac{\text{MHz}}{\text{V}}
$$

Das negative Vorzeichen bedeutet, dass die Ausgangsfrequenz mit steigender Abstimmspannung abnimmt.

Die Mittenfrequenz von ungefähr **5,5 MHz** wird bei einer Abstimmspannung von etwa **6,1 V** erreicht.

Für den gesamten Frequenzbereich von ungefähr **5 MHz bis 6 MHz** wird eine Spannungsänderung von etwa

$$
\Delta V_\text{tune} = 6{,}89\,\text{V} - 5{,}33\,\text{V} = 1{,}56\,\text{V}
$$

benötigt.

Bezogen auf den Arbeitspunkt bei ungefähr **6,1 V** entspricht dies einem benötigten Spannungshub von ungefähr:

$$
V_\text{tune}
\approx
6{,}1\,\text{V}
\pm
0{,}78\,\text{V}
$$

Der ursprünglich vorgesehene Eingangsspannungsbereich von ungefähr **±0,5 V** reicht daher ohne eine zusätzliche Anpassung nicht für den vollständigen Frequenzbereich aus.

### Gemessene Ausgangssignale

Die folgenden Abbildungen zeigen jeweils die letzten drei Perioden des mit dem Oszilloskop aufgenommenen Ausgangssignals.

#### Messung bei 5 MHz

<p align="center">
  <img
    src="python/plots/oszilloskop_5_MHz.png"
    alt="Oszilloskopmessung des Ausgangssignals bei 5 MHz"
    width="850">
</p>

<p align="center">
  <em>Gemessenes Ausgangssignal bei ungefähr 5 MHz</em>
</p>

#### Messung bei 5,5 MHz

<p align="center">
  <img
    src="python/plots/oszilloskop_5_5_MHz.png"
    alt="Oszilloskopmessung des Ausgangssignals bei 5,5 MHz"
    width="850">
</p>

<p align="center">
  <em>Gemessenes Ausgangssignal bei ungefähr 5,5 MHz</em>
</p>

#### Messung bei 6 MHz

<p align="center">
  <img
    src="python/plots/oszilloskop_6_MHz.png"
    alt="Oszilloskopmessung des Ausgangssignals bei 6 MHz"
    width="850">
</p>

<p align="center">
  <em>Gemessenes Ausgangssignal bei ungefähr 6 MHz</em>
</p>

Die gemessenen Signale besitzen über den untersuchten Frequenzbereich eine weitgehend sinusförmige Signalform.

Die Ausgangsamplitude ist bei **5 MHz** und **5,5 MHz** ähnlich groß. In Richtung **6 MHz** nimmt die Amplitude jedoch sichtbar ab. Die Ursache dafür muss im weiteren Projektverlauf noch untersucht werden.

### Simulation und Vergleich

Für die Frequenzen **5 MHz**, **5,5 MHz** und **6 MHz** wurden die simulierten Ausgangssignale mit den Oszilloskopmessungen verglichen.


<details>
  <summary><strong>Simulation und Vergleich bei 5 MHz anzeigen</strong></summary>

  #### Simulation bei 5 MHz

  <p align="center">
    <img
      src="python/plots/simulation_5_MHz.png"
      alt="Simuliertes Ausgangssignal bei 5 MHz"
      width="850">
  </p>

  #### Vergleich bei 5 MHz

  <p align="center">
    <img
      src="python/plots/vergleich_5_MHz.png"
      alt="Vergleich zwischen Simulation und Messung bei 5 MHz"
      width="900">
  </p>
</details>

<details>
  <summary><strong>Simulation und Vergleich bei 5,5 MHz anzeigen</strong></summary>

  #### Simulation bei 5,5 MHz

  <p align="center">
    <img
      src="python/plots/simulation_5_5_MHz.png"
      alt="Simuliertes Ausgangssignal bei 5,5 MHz"
      width="850">
  </p>

  #### Vergleich bei 5,5 MHz

  <p align="center">
    <img
      src="python/plots/vergleich_5_5_MHz.png"
      alt="Vergleich zwischen Simulation und Messung bei 5,5 MHz"
      width="900">
  </p>
</details>

<details>
  <summary><strong>Simulation und Vergleich bei 6 MHz anzeigen</strong></summary>

  #### Simulation bei 6 MHz

  <p align="center">
    <img
      src="python/plots/simulation_6_MHz.png"
      alt="Simuliertes Ausgangssignal bei 6 MHz"
      width="850">
  </p>

  #### Vergleich bei 6 MHz

  <p align="center">
    <img
      src="python/plots/vergleich_6_MHz.png"
      alt="Vergleich zwischen Simulation und Messung bei 6 MHz"
      width="900">
  </p>
</details>

Die normierten Vergleichsplots zeigen, dass Simulation und Messung grundsätzlich eine ähnliche periodische Signalform besitzen.

Es treten jedoch deutliche Unterschiede auf:

- Die Simulation besitzt einen großen Gleichspannungsanteil nahe der Versorgungsspannung.
- Das gemessene Signal liegt dagegen näherungsweise um 0 V.
- Die simulierte und die gemessene Ausgangsamplitude unterscheiden sich deutlich.
- Die Signalformen stimmen nicht vollständig überein.
- Bei 6 MHz nimmt die gemessene Ausgangsamplitude stärker ab.
- Kleine Phasenabweichungen bleiben trotz der Phasenanpassung sichtbar.

Die Simulation beschreibt damit das grundsätzliche Schwingverhalten, bildet den realen Arbeitspunkt und die tatsächliche Ausgangsamplitude jedoch nur eingeschränkt ab.

### Unterschiede zwischen Simulation und realem Aufbau

Für den NMOS-Stromspiegel werden in der Simulation und im realen Aufbau unterschiedliche Widerstandswerte benötigt.

Im realen Aufbau wird für `R4` ein Widerstand von **51 kΩ** verwendet. Bei größeren Widerständen ist der Strom zu gering, sodass der Oszillator nicht zuverlässig anschwingt.

In der SPICE-Simulation wird dagegen ein größerer Widerstand benötigt, da kleinere Widerstandswerte dort zu stärkeren Verzerrungen des Ausgangssignals führen.

Zusätzlich wurden im realen Aufbau Kondensatoren parallel zur Spannungsversorgung eingesetzt. Diese dienen als Abblock- und Stützkondensatoren und reduzieren hochfrequente Störungen sowie kurzzeitige Spannungsschwankungen.

Die Unterschiede zwischen Simulation und Messung können unter anderem durch folgende Einflüsse verursacht werden:

- vereinfachte SPICE-Modelle der MOSFETs
- vereinfachtes Kapazitätsmodell der Varaktordioden
- Bauteiltoleranzen
- parasitäre Kapazitäten und Induktivitäten
- Innenwiderstände der Induktivitäten
- Aufbau auf dem Steckbrett
- Leitungs- und Kontaktwiderstände
- Belastung durch Tastkopf und Oszilloskop
- Unterschiede bei der Versorgungsspannung
- Temperaturabhängigkeit der Bauteile

### Platinenlayout

Eine erste Platine wurde bereits in KiCad erstellt. Das Layout muss jedoch noch an den aktuellen Schaltungsstand angepasst und weiter optimiert werden.

Besonders berücksichtigt werden müssen:

- Platzierung der Abblockkondensatoren nahe an den MOSFETs
- Entkopplung des Ausgangs vom Schwingkreis
- Ein- und Ausgangsanpassung
- mögliche Ausgangspufferung

## Noch nicht vollständig erfüllte Anforderungen

Folgende Anforderungen sind derzeit noch nicht vollständig umgesetzt oder müssen weiter untersucht werden:

- Anpassung des Modulationseingangs an ein Eingangssignal von ungefähr **±0,5 V**
- Untersuchung der Bandbreite des Modulationseingangs
- weitere Stabilisierung der Ausgangsamplitude in Richtung **6 MHz**
- Einkopplung des Modulationssignals zusammen mit einer einstellbaren Gleichspannung
- Anpassung des Eingangs auf **50 Ω**
- Ergänzung einer Ausgangspufferung zur Entkopplung des Schwingkreises
- Anpassung des Ausgangs auf **50 Ω**
- möglichst kurzschlusssichere Auslegung des Ausgangs
- Untersuchung der Frequenzdrift und der Temperaturabhängigkeit
- Anpassung und Optimierung des Platinenlayouts
- Aufbau und Prüfung der endgültigen Platine

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