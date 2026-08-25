import json
import sys

def capture_speed_data():
    """Liest JSON-Daten vom Roboter (stdin) und speichert sie in speed_data.json"""
    
    speed_data = []
    
    print("Warte auf Daten vom Roboter...")
    print("(Drücke Ctrl+C zum Beenden)")
    
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                
                # Prüfen ob es Speed-Daten sind (haben time, speed, distance)
                if 'time' in data and 'speed' in data and 'distance' in data:
                    speed_data.append(data)
                    print(f"Empfangen: Zeit={data['time']}ms, Speed={data['speed']}, Distanz={data['distance']:.2f}mm")
                
            except json.JSONDecodeError:
                # Ignoriere Zeilen die kein JSON sind
                continue
                
    except KeyboardInterrupt:
        print("\n\nDatenerfassung beendet.")
    
    # Daten speichern
    if speed_data:
        with open("../../data/speed_data.json", "w") as f:
            json.dump(speed_data, f, indent=2)
        print(f"\n{len(speed_data)} Datenpunkte in '../../data/speed_data.json' gespeichert.")
        print("\nJetzt kannst du 'python speed_data.py' ausführen um den Plot zu erstellen.")
    else:
        print("\nKeine Daten empfangen.")

if __name__ == "__main__":
    capture_speed_data()
