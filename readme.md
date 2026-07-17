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



## Schaltungsprinzip

Der aktuelle VCO basiert auf einer differentiellen Cross-Coupled-Oszillatorschaltung mit vier NMOS-Transistoren.

Die Schaltung besteht im Wesentlichen aus:

- zwei gekreuzt gekoppelten NMOS-Transistoren `Q1` und `Q2`
- zwei NMOS-Transistoren `Q3` und `Q4` als Stromspiegel
- zwei Induktivitäten `L1` und `L2`
- zwei Varaktordioden `D1` und `D2`
- einem Widerstand `R4` zur Einstellung des Referenzstroms
- einer Versorgungsspannung `VDD`
- einer Abstimmspannung `Vtune`

## Cross-Coupled-Oszillator

Die Transistoren `Q1` und `Q2` sind über Kreuz gekoppelt. Das Gate jedes Transistors ist mit dem Drain des jeweils anderen Transistors verbunden.

Durch diese Rückkopplung entsteht ein negativer differentieller Widerstand. Dieser gleicht die Verluste des LC-Schwingkreises aus und ermöglicht das dauerhafte Schwingen der Schaltung.

Die Ausgangsspannung kann an einem der beiden differentiellen Schwingkreisknoten abgegriffen werden. Im aktuellen Schaltplan wird das Ausgangssignal am rechten Schwingkreisknoten ausgegeben.

## Schwingkreis

Der frequenzbestimmende Schwingkreis besteht aus:

- `L1 = 3,3 µH`
- `L2 = 3,3 µH`
- `D1 = 1SV149`
- `D2 = 1SV149`

Die beiden Induktivitäten sind mit der Versorgungsspannung verbunden. Die Varaktordioden befinden sich zwischen den beiden differentiellen Ausgangsknoten.

Der gemeinsame Anschluss der Varaktordioden wird über die Spannung `Vtune` angesteuert.

Die Resonanzfrequenz kann vereinfacht mit folgender Gleichung beschrieben werden:

$$
f_0 = \frac{1}{2\pi\sqrt{L \cdot C}}
$$

Dabei ist:

- $L$ die wirksame Induktivität des Schwingkreises
- $C$ die wirksame Kapazität der Varaktordioden einschließlich parasitärer Kapazitäten

Da die Kapazität der Varaktordioden von der angelegten Sperrspannung abhängt, kann die Ausgangsfrequenz über `Vtune` verändert werden.

## Varaktordioden

Als Varaktordioden werden zwei Dioden vom Typ `1SV149` verwendet.

Die Dioden sind gegensinnig beziehungsweise back-to-back angeordnet. Dadurch soll verhindert werden, dass eine der Dioden durch die hochfrequente Schwingung dauerhaft in Durchlassrichtung betrieben wird.

Eine Änderung der Abstimmspannung `Vtune` verändert die Sperrspannung der Dioden. Damit ändert sich ihre Kapazität und somit die Resonanzfrequenz des Schwingkreises.

Für die Simulation wird ein eigenes SPICE-Modell der `1SV149` verwendet, da die Diode nicht standardmäßig in ngspice enthalten ist.

## Stromquelle

Die Transistoren `Q3` und `Q4` bilden zusammen mit `R4` einen einfachen NMOS-Stromspiegel.

`Q4` ist als Referenztransistor beschaltet. Über den Widerstand `R4` wird ein Referenzstrom eingestellt. Dieser Strom wird über `Q3` gespiegelt und als gemeinsamer Strom für das Cross-Coupled-Transistorpaar verwendet.

Der Stromspiegel hat folgende Aufgaben:

- Einstellung des Arbeitspunktes
- Begrenzung des Stroms durch den Oszillator
- Reduzierung großer Amplitudenschwankungen
- Verringerung der Abhängigkeit von der Versorgungsspannung
- Schutz der Transistoren vor zu hohen Strömen

Der Stromspiegel stellt jedoch keine vollständige automatische Amplitudenregelung dar. Die Ausgangsamplitude kann sich weiterhin mit der Frequenz, der Abstimmspannung und der Belastung verändern.

## Abstimmspannung

Die Ausgangsfrequenz wird über die Gleichspannung `Vtune` eingestellt.

Für den späteren Einsatz als Frequenzmodulator soll die Abstimmspannung aus zwei Anteilen bestehen:

$$
V_\text{tune}(t) = V_\text{DC} + v_\text{in}(t)
$$

Dabei ist:

- `VDC` eine einstellbare Gleichspannung zur Festlegung der Mittenfrequenz
- `vin(t)` das zu modulierende Eingangssignal

Die Gleichspannung ermöglicht außerdem eine Korrektur von Frequenzabweichungen und Frequenzdrift.

## Frequenzkennlinie

Zur Untersuchung des VCOs soll die Ausgangsfrequenz in Abhängigkeit von der Abstimmspannung aufgenommen werden.

Dazu wird `Vtune` schrittweise verändert und für jeden Spannungswert die Ausgangsfrequenz gemessen.

Die Kennlinie wird anschließend als

$$
f_\text{out} = f(V_\text{tune})
$$

dargestellt.

Aus der Kennlinie können unter anderem folgende Eigenschaften bestimmt werden:

- erreichbarer Frequenzbereich
- Mittenfrequenz
- VCO-Empfindlichkeit
- Linearität
- nichtlineare Abweichung
- geeigneter Arbeitspunkt

Die VCO-Empfindlichkeit ergibt sich näherungsweise aus:

$$
K_\text{VCO} = \frac{\Delta f}{\Delta V}
$$

und wird beispielsweise in `MHz/V` angegeben.

## Ein- und Ausgang

Der spätere Platinenaufbau soll jeweils eine BNC-Buchse für den Eingang und den Ausgang besitzen.

### Eingang

Über den Eingang werden die Gleichspannung zur Frequenzeinstellung und das Modulationssignal eingespeist.

Der Eingang soll:

- für ein Signal von ungefähr ±0,5 V geeignet sein
- eine Gleichspannung zur Einstellung der Mittenfrequenz ermöglichen
- möglichst gering auf die Signalquelle zurückwirken
- auf 50 Ω angepasst werden

### Ausgang

Am Ausgang soll das erzeugte hochfrequente Signal messbar sein.

Der Ausgang soll:

- auf 50 Ω angepasst werden
- mit einem Oszilloskop oder Spektrumanalysator messbar sein
- den Schwingkreis möglichst wenig belasten
- möglichst kurzschlusssicher ausgeführt werden

Im aktuellen Schaltplan ist noch keine vollständige 50-Ω-Ausgangsanpassung beziehungsweise Ausgangspufferung dargestellt. Diese muss für den endgültigen Aufbau noch ergänzt und untersucht werden.

## Verwendete Bauteile

Für den aktuellen Aufbau werden unter anderem folgende Bauteile verwendet:

| Bezeichnung | Bauteil | Funktion |
|---|---|---|
| Q1, Q2 | BS170 | Cross-Coupled-Transistorpaar |
| Q3, Q4 | BS170 | Stromspiegel beziehungsweise Stromquelle |
| D1, D2 | 1SV149 | Frequenzabstimmung |
| L1, L2 | 3,3 µH | Induktiver Teil des Schwingkreises |
| R4 | 51 kΩ | Einstellung des Referenzstroms |

Die Bauteilwerte können sich während der weiteren Entwicklung noch ändern.

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

Die SPICE-Simulation bildet die reale Schaltung nur näherungsweise ab.

Mögliche Ursachen für Abweichungen sind:

- vereinfachtes SPICE-Modell der Varaktordioden
- Abweichungen der MOSFET-Modelle
- Bauteiltoleranzen
- parasitäre Kapazitäten
- parasitäre Induktivitäten
- Widerstände der Induktivitäten
- Leiterbahnlängen
- Steckverbindungen
- Eigenschaften der Spannungsversorgung
- Belastung durch Tastköpfe und Messgeräte
- Temperaturabhängigkeit der Bauteile

Besonders das Kapazitäts-Spannungs-Verhalten der Varaktordioden hat einen großen Einfluss auf den erreichbaren Frequenzbereich.

## Aktueller Stand

Der aktuelle Entwicklungsstand umfasst:

- Aufbau eines differentiellen Cross-Coupled-VCOs
- Verwendung von zwei BS170 als Oszillatortransistoren
- Stromquelle mit NMOS-Stromspiegel
- zwei Induktivitäten mit jeweils 3,3 µH
- Frequenzabstimmung mit zwei 1SV149-Varaktordioden
- Einbindung eines eigenen SPICE-Modells
- Simulation der Schaltung in KiCad mit ngspice
- Untersuchung des Frequenzbereichs von ungefähr 5 MHz bis 6 MHz
- Vergleich zwischen Simulation und realem Aufbau

Noch zu untersuchen beziehungsweise umzusetzen sind:

- genaue Aufnahme der Frequenzkennlinie
- Bestimmung der Nichtlinearität
- endgültige Dimensionierung der Stromquelle
- Stabilisierung der Ausgangsamplitude
- 50-Ω-Anpassung des Eingangs
- 50-Ω-Anpassung des Ausgangs
- Ausgangspufferung
- Kurzschlussschutz
- Aufbau und Messung der endgültigen Platine

## Software

Für das Projekt werden folgende Programme verwendet:

- KiCad
- ngspice
- Git
- GitHub

## Projekt öffnen

Das Repository kann mit folgendem Befehl geklont werden:

```bash
git clone <URL-DES-REPOSITORY>
```

Anschließend kann das KiCad-Projekt über die entsprechende `.kicad_pro`-Datei geöffnet werden.

Vor der Simulation sollte überprüft werden, ob:

- alle Symbolbibliotheken vorhanden sind
- alle Footprints korrekt zugeordnet sind
- das SPICE-Modell der 1SV149 eingebunden ist
- die Modellpfade in KiCad korrekt eingestellt sind

## Mitwirkende

- Maurice Draeger
- Ethaniel König