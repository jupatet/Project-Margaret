import json
import matplotlib.pyplot as plt

def collect_speed_data(json_file="../../data/speed_data.json"):
    """Liest die Geschwindigkeitsdaten aus einer JSON-Datei und erstellt einen Plot"""
    
    # JSON-Datei einlesen
    try:
        with open(json_file, 'r') as f:
            # Prüfe ob es ein Array oder mehrere Zeilen mit JSON-Objekten ist
            content = f.read().strip()
            if not content:
                print(f"Fehler: Datei {json_file} ist leer!")
                return
            
            # Wenn es mit [ beginnt, ist es ein Array
            if content.startswith('['):
                data = json.loads(content)
            else:
                # Sonst: jede Zeile ist ein JSON-Objekt
                data = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                            
    except FileNotFoundError:
        print(f"Fehler: Datei {json_file} nicht gefunden!")
        return
    
    # Prüfen ob Daten vorhanden sind
    if not data:
        print("Keine gültigen Daten in der Datei gefunden!")
        return
    
    # Daten extrahieren
    timestamps = [entry['time'] for entry in data]
    speeds = [entry['speed'] for entry in data]
    distances = [entry['distance'] for entry in data]
    
    # Plot erstellen
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Geschwindigkeit über Zeit
    ax1.plot(timestamps, speeds, 'b-', linewidth=2)
    ax1.set_xlabel('Zeit (ms)', fontsize=12)
    ax1.set_ylabel('Geschwindigkeit (mm/s)', fontsize=12)
    ax1.set_title('Geschwindigkeit über Zeit', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Geschwindigkeit über Distanz
    ax2.plot(distances, speeds, 'r-', linewidth=2)
    ax2.set_xlabel('Distanz (mm)', fontsize=12)
    ax2.set_ylabel('Geschwindigkeit (mm/s)', fontsize=12)
    ax2.set_title('Geschwindigkeit über Distanz', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../speed_plot.png', dpi=300)
    plt.show()
    
    print(f"Plot gespeichert als '../speed_plot.png'")
    print(f"Anzahl Datenpunkte: {len(data)}")
    print(f"Max. Geschwindigkeit: {max(speeds):.2f} mm/s")
    print(f"Min. Geschwindigkeit: {min(speeds):.2f} mm/s")
    print(f"Durchschnittsgeschwindigkeit: {sum(speeds)/len(speeds):.2f} mm/s")

if __name__ == "__main__":
    collect_speed_data()
