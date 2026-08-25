"""
PID Tuner Results Visualizer
Zeigt die Ergebnisse des PID-Tunings an
"""

import matplotlib.pyplot as plt
import json
import os

def visualize_pid_tuning(filename='../../data/pid_tuning_results.json'):
    """
    Visualisiert die Ergebnisse des PID-Tunings
    """
    if not os.path.exists(filename):
        print(f"ERROR: File '{filename}' not found!")
        print("Please run the PID tuner first.")
        return
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse JSON file: {e}")
        return
    
    if not data:
        print("WARNING: No data found in file!")
        return
    
    print("="*60)
    print("PID TUNING RESULTS")
    print("="*60)
    
    # PID-Parameter anzeigen
    params = data.get('parameters', {})
    method = data.get('method', 'Unknown')
    
    print(f"\nMethode: {method}")
    print(f"\nOptimale PID-Parameter:")
    print(f"  Kp = {params.get('Kp', 0):.6f}")
    print(f"  Ki = {params.get('Ki', 0):.6f}")
    print(f"  Kd = {params.get('Kd', 0):.6f}")
    
    # System-Charakteristiken
    sys_char = data.get('system_characteristics', {})
    print(f"\nSystem-Charakteristiken:")
    print(f"  Ultimate Gain (Ku) = {sys_char.get('Ku', 0):.3f}")
    print(f"  Ultimate Period (Tu) = {sys_char.get('Tu', 0):.3f}s")
    print(f"  Durchschn. Fehler = {sys_char.get('avg_error', 0):.2f}°")
    print(f"  Max. Fehler = {sys_char.get('max_error', 0):.2f}°")
    
    # Test-Ergebnisse
    test_results = data.get('test_results', {})
    print(f"\nTest-Ergebnisse:")
    print(f"  Anzahl Fahrten = {test_results.get('runs', 0)}")
    print(f"  Drehfehler = {test_results.get('turn_error', 0):.2f}°")
    
    # Visualisierung erstellen
    fig = plt.figure(figsize=(14, 8))
    
    # Subplot 1: PID-Parameter als Balkendiagramm
    ax1 = plt.subplot(2, 2, 1)
    param_names = ['Kp', 'Ki', 'Kd']
    param_values = [params.get(name, 0) for name in param_names]
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    bars = ax1.bar(param_names, param_values, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Wert', fontsize=11)
    ax1.set_title('Berechnete PID-Parameter', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Werte auf Balken schreiben
    for bar, value in zip(bars, param_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.4f}',
                ha='center', va='bottom', fontsize=10)
    
    # Subplot 2: System-Charakteristiken
    ax2 = plt.subplot(2, 2, 2)
    char_names = ['Ku\n(Ult. Gain)', 'Tu\n(Ult. Period)', 'Avg Error\n(Degrees)', 'Max Error\n(Degrees)']
    char_values = [
        sys_char.get('Ku', 0),
        sys_char.get('Tu', 0) * 10,  # Skalierung für bessere Darstellung
        sys_char.get('avg_error', 0),
        sys_char.get('max_error', 0)
    ]
    char_colors = ['#9b59b6', '#f39c12', '#1abc9c', '#e67e22']
    
    bars2 = ax2.bar(range(len(char_names)), char_values, color=char_colors, alpha=0.7, edgecolor='black')
    ax2.set_xticks(range(len(char_names)))
    ax2.set_xticklabels(char_names, fontsize=9)
    ax2.set_ylabel('Wert', fontsize=11)
    ax2.set_title('System-Charakteristiken', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # Werte auf Balken
    for i, (bar, value) in enumerate(zip(bars2, char_values)):
        height = bar.get_height()
        display_value = value / 10 if i == 1 else value  # Tu zurückskalieren
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{display_value:.3f}',
                ha='center', va='bottom', fontsize=9)
    
    # Subplot 3: Vergleich mit optimierten Werten
    ax3 = plt.subplot(2, 2, 3)
    
    # Wenn es optimierte Werte gibt, vergleichen
    optimized_kp = 1.968685
    optimized_ki = 0.1223187
    optimized_kd = 0.1041346
    
    x = range(3)
    width = 0.35
    
    bars_new = ax3.bar([i - width/2 for i in x], param_values, width, 
                       label='Neu berechnet', color='#3498db', alpha=0.7, edgecolor='black')
    bars_opt = ax3.bar([i + width/2 for i in x], [optimized_kp, optimized_ki, optimized_kd], width,
                       label='Bisherige Werte', color='#95a5a6', alpha=0.7, edgecolor='black')
    
    ax3.set_ylabel('Wert', fontsize=11)
    ax3.set_title('Vergleich: Neu vs. Bisherig', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(param_names)
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    
    # Subplot 4: Zusammenfassung als Text
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    
    summary_text = f"""
    PID AUTO-TUNING ZUSAMMENFASSUNG
    ═══════════════════════════════════
    
    Methode: {method}
    
    EMPFOHLENE PARAMETER:
    ─────────────────────────────────
    Kp = {params.get('Kp', 0):.6f}
    Ki = {params.get('Ki', 0):.6f}
    Kd = {params.get('Kd', 0):.6f}
    
    PERFORMANCE:
    ─────────────────────────────────
    Durchschn. Fehler: {sys_char.get('avg_error', 0):.2f}°
    Max. Fehler: {sys_char.get('max_error', 0):.2f}°
    Drehfehler (180°): {test_results.get('turn_error', 0):.2f}°
    
    TEST-INFO:
    ─────────────────────────────────
    Anzahl Testfahrten: {test_results.get('runs', 0)}
    Ultimate Gain (Ku): {sys_char.get('Ku', 0):.3f}
    Ultimate Period (Tu): {sys_char.get('Tu', 0):.3f}s
    
    Diese Parameter in roboter.py eintragen!
    """
    
    ax4.text(0.1, 0.5, summary_text, 
            fontsize=10,
            verticalalignment='center',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    # Speichern
    output_file = filename.replace('.json', '.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nDiagramm gespeichert: {output_file}")
    
    # Anzeigen
    plt.show()
    
    print("\n" + "="*60)
    print("VISUALISIERUNG ABGESCHLOSSEN")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = '../../data/pid_tuning_results.json'
    
    print("PID Tuner Results Visualizer")
    print(f"Lade Daten aus: {filename}\n")
    
    visualize_pid_tuning(filename)
