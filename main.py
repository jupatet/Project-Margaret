#Import robot hardware and functions
from programs.roboter import hub, left_motor, right_motor, axle_track, wheel_diameter, motor_F, motor_B, drive_forward, wheel_circumference, get_drive_base, drive_backward, turn_left, turn_right, set_current_module, print_heading_log, reset_heading_log
from pybricks.parameters import Stop, Button, Port
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

# Zeige den Akkustand an
battery_voltage = hub.battery.voltage()
print("Akkustand (Spannung):", battery_voltage, "mV")

# Liste aller verfügbaren Module
MODULES = ["Green", "Red", "Blue", "Yellow", "Black", "Colourless"]

def select_module():
    """Modul per Knopfdruck auswählen.
    LEFT / RIGHT = durchblättern, CENTER = bestätigen"""
    # Wait for any held buttons to be released
    while hub.buttons.pressed():
        wait(10)

    index = 0
    print("Modul waehlen (LEFT/RIGHT = blaettern, CENTER = bestaetigen):")
    print(f"[{index+1}/{len(MODULES)}] {MODULES[index]}")

    while True:
        pressed = hub.buttons.pressed()

        if Button.LEFT in pressed:
            index = (index - 1) % len(MODULES)
            print(f"[{index+1}/{len(MODULES)}] {MODULES[index]}")
            while Button.LEFT in hub.buttons.pressed():
                wait(10)

        elif Button.RIGHT in pressed:
            index = (index + 1) % len(MODULES)
            print(f"[{index+1}/{len(MODULES)}] {MODULES[index]}")
            while Button.RIGHT in hub.buttons.pressed():
                wait(10)

        elif Button.CENTER in pressed:
            module_name = MODULES[index]
            print(f"Modul gewaehlt: {module_name}")
            while Button.CENTER in hub.buttons.pressed():
                wait(10)
            return module_name

        wait(50)

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
print("LEFT/RIGHT = Modul waehlen, CENTER = starten")

# Start stopwatch for first module (no switching time before first module)
stopwatch.reset()

while True:
    # Modul per Knopfdruck auswaehlen
    module_name = select_module()

    # Get switching time (includes module-selection time)
    if len(timing_data) > 0:
        switching_time = stopwatch.time()/1000
        stopwatch.reset()
    else:
        switching_time = 0
        stopwatch.reset()
    
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
    
    if module_result is not None:
        print(f"{module_name} fertig: {module_time} s")
        
        # Speichere Zeit mit Zähler für mehrfache Ausführungen
        timing_key = f"{module_name}_{module_counter[module_name]}"
        timing_data[timing_key] = module_time
        program_time += module_time
        
        # Prüfe ob Programm beendet werden soll
        if module_result == True and module_name == "Colourless":
            # Lock in total time right here — stopwatch is NOT reset
            timing_data["Total"] = program_time
            print("Programm wird beendet...")
            print("Program done:", program_time, "s")
            
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
    
    stopwatch.reset()  # Reset for next switching time measurement
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