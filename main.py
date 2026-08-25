#Import robot hardware and functions
from programs.roboter import hub, left_motor, right_motor, axle_track, wheel_diameter, motor_F, motor_B, drive_forward, wheel_circumference, get_drive_base, drive_backward, turn_left, turn_right, set_current_module, print_heading_log, reset_heading_log
from pybricks.parameters import Stop, Button, Color, Port
from pybricks.pupdevices import ColorSensor
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
from programs.Code_Yellow import Yellow
from programs.Code_Green import Green
from programs.Code_Red import Red
from programs.Code_Blue import Blue
from programs.Code_Black import Black
from programs.Code_Colourless import Colourless
import ujson as json
import umath as math

hub.system.set_stop_button(Button.BLUETOOTH)  

try:
    color_sensor = ColorSensor(Port.C)
    print("Farbsensor initialisiert")
except:
    print("WARNUNG: Farbsensor nicht gefunden! Bitte Port prüfen.")
    color_sensor = None

# Zeige den Akkustand an
battery_voltage = hub.battery.voltage()
print("Akkustand (Spannung):", battery_voltage, "mV")

# Funktion zur Farberkennung und Modulzuordnung
def detect_module():
    """Erkennt die Farbe und gibt den Modulnamen zurück"""
    if color_sensor is None:
        print("Kein Farbsensor verfügbar!")
        return None
    
    detected_color = color_sensor.color()
    
    print("Erkannte Farbe:", detected_color)
    
    # Farbzuordnung zu Modulen
    color_to_module = {
        Color.GREEN: "Green",
        Color.RED: "Red",
        Color.BLUE: "Blue",
        Color.YELLOW: "Yellow",
        Color.WHITE: "Colourless",
        Color.NONE: "Black"
    }
    
    module_name = color_to_module.get(detected_color, None)
    if module_name:
        print("Modul erkannt:", module_name)
    else:
        print("Unbekannte Farbe:", detected_color)
    
    return module_name

# Funktion zum Ausführen eines Moduls basierend auf Namen
def run_module(module_name):
    """Führt das entsprechende Modul aus"""
    if module_name == "Green":
        Green()
        return True
    elif module_name == "Red":
        Red()
        return True
    elif module_name == "Blue":
        Blue()
        return True
    elif module_name == "Yellow":
        Yellow()
        return True
    elif module_name == "Black":
        Black()
        return True
    elif module_name == "Colourless":
        result = Colourless()
        return result  # Gibt True zurück wenn Programm beendet werden soll
    else:
        print("Unbekanntes Modul:", module_name)
        return False

# Hauptprogramm
stopwatch = StopWatch()
program_time = 0
timing_data = {}
module_counter = {}

print("=== Roboter bereit ===")
print("Drücke LEFT oder RIGHT-Button zum Starten eines Moduls")

# Start stopwatch for first module (no switching time before first module)
stopwatch.reset()

while True:
    # Warte auf LEFT oder RIGHT-Button
    pressed = hub.buttons.pressed()
    while not pressed or (Button.LEFT not in pressed and Button.RIGHT not in pressed):
        wait(10)
        pressed = hub.buttons.pressed()
    
    # Get switching time if this is not the first module
    # This includes human handling time (swapping modules, pressing button)
    if len(timing_data) > 0:
        switching_time = stopwatch.time()/1000
        stopwatch.reset()
    else:
        # First module - no switching time, just reset
        switching_time = 0
        stopwatch.reset()
    
    # Modul durch Farberkennung identifizieren
    module_name = detect_module()
    
    if module_name is None:
        print("Kein Modul erkannt! Bitte Modul aufsetzen.")
        continue
    
    # Zähle wie oft dieses Modul schon ausgeführt wurde
    if module_name not in module_counter:
        module_counter[module_name] = 0
    module_counter[module_name] += 1
    
    # Speichere Switching Time (außer beim ersten Durchlauf)
    if len(timing_data) > 0:
        switch_key = f"Switch_to_{module_name}_{module_counter[module_name]}"
        timing_data[switch_key] = switching_time
        program_time += switching_time
        print(f"Switching time: {switching_time} s")
    
    # Modul ausführen
    set_current_module(f"{module_name}_{module_counter[module_name]}")
    print(f"Starte {module_name}...")
    module_result = run_module(module_name)
    module_time = stopwatch.time()/1000
    stopwatch.reset()  # Reset for next switching time measurement
    
    if module_result is not None:
        print(f"{module_name} fertig: {module_time} s")
        
        # Speichere Zeit mit Zähler für mehrfache Ausführungen
        timing_key = f"{module_name}_{module_counter[module_name]}"
        timing_data[timing_key] = module_time
        program_time += module_time
        
        # Prüfe ob Programm beendet werden soll
        if module_result == True and module_name == "Colourless":
            print("Programm wird beendet...")
            print("Program done:", program_time, "s")
            timing_data["Total"] = program_time
            
            # Ask user if they want to save the data using hub buttons
            print("Press LEFT button to save data")
            print("Press any other button to skip")
            
            # Wait for button press
            while True:
                pressed = hub.buttons.pressed()
                if pressed:
                    if Button.LEFT in pressed:
                        # Print timing data in JSON format for PowerShell script
                        print("===JSON_START===")
                        print(json.dumps(timing_data))
                        print("===JSON_END===")
                        print("===HEADING_START===")
                        print_heading_log()
                        print("===HEADING_END===")
                        print("Data ready for saving")
                    else:
                        print("Data not saved")
                    break
                wait(10)
            
            raise SystemExit
    else:
        print("Fehler beim Ausführen des Moduls")
    
    print("Bereit für nächstes Modul...")

# Total Program Time
print("Program done:", program_time, "s")
timing_data["Total"] = program_time

# Ask user if they want to save the data using hub buttons
print("Press LEFT button to save data")
print("Press any other button to skip")

# Wait for button press
while True:
    pressed = hub.buttons.pressed()
    if pressed:
        if Button.LEFT in pressed:
            # Print timing data in JSON format for PowerShell script
            print("===JSON_START===")
            print(json.dumps(timing_data))
            print("===JSON_END===")
            print("===HEADING_START===")
            print_heading_log()
            print("===HEADING_END===")
            print("Data ready for saving")
        else:
            print("Data not saved")
        break
    wait(10)