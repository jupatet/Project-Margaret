# FLL Run Timer

Misst und analysiert automatisch die Zeit für jeden Programm-Abschnitt eines FLL-Laufs. Nach dem Lauf gibt es Diagramme, die zeigen wie lange jedes Modul gedauert hat – und wie sich die Zeiten über mehrere Läufe entwickeln.

---

## Einrichtung

### 1. Eigene Module eintragen
Der Timer ruft sechs Modulfunktionen aus dem Ordner `programs/` auf:

| Datei | Funktion | Wofür |
|---|---|---|
| `programs/Code_Green.py` | `Green()` | Modul Green |
| `programs/Code_Red.py` | `Red()` | Modul Red |
| `programs/Code_Blue.py` | `Blue()` | Modul Blue |
| `programs/Code_Yellow.py` | `Yellow()` | Modul Yellow |
| `programs/Code_Black.py` | `Black()` | Modul Black |
| `programs/Code_Colourless.py` | `Colourless()` | **Letztes Modul – beendet den Lauf** |

Den vorhandenen Roboter-Code einfach in die jeweilige Funktion einfügen. `Colourless()` muss `True` zurückgeben – das signalisiert dem Timer, dass der Lauf vorbei ist.

### 2. Hub-Namen einstellen
`run_python.ps1` öffnen und den Bluetooth-Namen des Hubs eintragen:

```powershell
param(
    [string]$RobotName = "euer-hub-name",   # <-- hier anpassen
    ...
)
```

---

## Einen Lauf aufzeichnen

### Schritt 1 – Workflow starten
PowerShell im Projektordner öffnen und ausführen:

```powershell
.\run_python.ps1
```

Das Skript verbindet sich per Bluetooth mit dem Hub, überträgt `main.py` und startet das Programm.

### Schritt 2 – Module am Hub auswählen und starten

Sobald der Hub bereit ist, mit den **Hub-Tasten** die Module nacheinander auswählen und starten:

| Taste | Funktion |
|---|---|
| **RIGHT** | Nächstes Modul |
| **LEFT** | Vorheriges Modul |
| **CENTER** | ✅ Bestätigen – Modul starten |
| **Bluetooth** | ⛔ Programm abbrechen |

Die aktuelle Auswahl wird in der Konsole angezeigt, z. B. `[3/6] Blue`.

> **Wichtig:** Den Lauf immer mit **Colourless** beenden – nur das stoppt die Zeitmessung und speichert die Ergebnisse.

### Schritt 3 – Daten speichern
Nachdem Colourless fertig ist, fragt der Hub ob gespeichert werden soll:

- **LEFT** drücken → Daten werden gespeichert, Diagramme werden geöffnet
- **Beliebige andere Taste** → Lauf wird verworfen

### Schritt 4 – Diagramme ansehen
Das Skript öffnet die Diagramme automatisch. Alternativ können sie manuell gestartet werden:

```powershell
python data_analysis\timing_diagram.py
```

Zur Auswahl stehen:
1. **Balkendiagramm** – Zeiten des letzten Laufs
2. **Verlaufsdiagramm** – Vergleich über alle gespeicherten Läufe
3. **Tortendiagramm** – Zeitverteilung des letzten Laufs
4. **Alle Diagramme** auf einmal

Die Diagramme werden außerdem als PNG-Dateien im Projektordner gespeichert.

---

## Wie die Zeitmessung funktioniert

| Was gemessen wird | Start | Stop |
|---|---|---|
| **Modulzeit** | CENTER gedrückt (Modul startet) | Modulfunktion kehrt zurück |
| **Wechselzeit** | Vorheriges Modul endet | CENTER für nächstes Modul gedrückt |
| **Gesamt** | Erstes Modul startet | Letztes Modul (Colourless) endet |

Die Wechselzeit beinhaltet auch die Zeit zum Durchblättern der Modulliste – das ist gewollt, da es die echte Handling-Zeit widerspiegelt.

---

## Gespeicherte Dateien

Alle Daten werden im Ordner `data/` gespeichert und bei jedem Lauf ergänzt – nichts wird überschrieben.

| Datei | Inhalt |
|---|---|
| `data/timing_data.json` | Modul- und Wechselzeiten aller Läufe |
| `data/heading_data.json` | Gyro-Ausrichtungsprotokoll pro Lauf |

---

## Modulliste anpassen

Um Module hinzuzufügen, zu entfernen oder umzubenennen, die `MODULES`-Liste am Anfang von `main.py` bearbeiten:

```python
MODULES = ["Green", "Red", "Blue", "Yellow", "Black", "Colourless"]
```

Für jeden Eintrag muss eine passende Datei `programs/Code_<Name>.py` existieren sowie ein entsprechender Fall in der Funktion `run_module()` weiter unten.
