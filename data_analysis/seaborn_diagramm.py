"""
FLL Timing-Daten Visualisierung
================================
Lädt timing_data.json und erstellt verschiedene Seaborn-Plots:
  1. Barplot   – Durchschnittszeiten pro Event (± Standardabweichung)
  2. Boxplot   – Verteilung & Ausreißer pro Event
  3. Violin    – Dichteform + einzelne Messpunkte (Swarm)
  4. Switch-Boxplot – nur die menschlichen Wechselzeiten
  5. Gestapelte Balken – Zusammensetzung jedes Laufs
  6. Gantt-Timeline – sequentielle Darstellung pro Lauf
  7. Heatmap   – Korrelation zwischen Events
  8. Total-Scatterplot – Gesamtzeit pro Lauf
  9. Pie-Chart – Zeitanteile letzter Lauf
 10. Barplot – Zeiten letzter Lauf
 11. Modul vs. Switch – Zusammenfassung letzter Lauf
 12. Heading über Distanz – letzter Lauf (alle Segmente)
 13. Heading-Abweichung pro Modul – Boxplot über alle Läufe
 14. Max-Heading pro Segment – letzter Lauf
"""

import json
import pathlib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Konfiguration ────────────────────────────────────────────────
DATA_FILE = pathlib.Path(__file__).parent.parent / "data" / "timing_data.json"
SAVE_DIR = pathlib.Path(__file__).parent.parent / "plots"
SAVE_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=1.1)

# Farben für Module vs. Switches
MODULE_COLOR = "#4C72B0"
SWITCH_COLOR = "#DD8452"

# ── Daten laden ──────────────────────────────────────────────────
with open(DATA_FILE, "r", encoding="utf-8-sig") as f:
    raw = json.load(f)

df = pd.DataFrame(raw)
df.index.name = "Lauf"
df = df.reset_index()
df["Lauf"] = df["Lauf"] + 1  # 1-basiert

# Long-Format (ohne Total)
df_long = (
    df.melt(id_vars="Lauf", var_name="Event", value_name="Zeit")
    .dropna(subset=["Zeit"])
)
df_long["Typ"] = df_long["Event"].apply(
    lambda e: "Switch (Mensch)" if e.startswith("Switch") else (
        "Total" if e == "Total" else "Modul (Roboter)"
    )
)

# Events ohne Total, sortiert nach Mittelwert
events_no_total = df_long[df_long["Event"] != "Total"]
order = (
    events_no_total.groupby("Event")["Zeit"]
    .mean()
    .sort_values()
    .index.tolist()
)

# ── Hilfsfunktion ────────────────────────────────────────────────
def save_and_show(fig, name):
    path = SAVE_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  ✓ {path}")
    plt.close(fig)


# ── 1) Barplot – Durchschnitt ± SD ──────────────────────────────
print("\n1) Barplot – Durchschnittszeiten")
fig, ax = plt.subplots(figsize=(12, 5))
palette = [SWITCH_COLOR if "Switch" in e else MODULE_COLOR for e in order]
sns.barplot(
    data=events_no_total, x="Event", y="Zeit",
    order=order, errorbar="sd", palette=palette, ax=ax, edgecolor="black",
)
ax.set_title("Durchschnittliche Dauer pro Event (± SD)")
ax.set_ylabel("Sekunden")
ax.set_xlabel("")
plt.xticks(rotation=45, ha="right")
# Legende
patches = [
    mpatches.Patch(color=MODULE_COLOR, label="Modul (Roboter)"),
    mpatches.Patch(color=SWITCH_COLOR, label="Switch (Mensch)"),
]
ax.legend(handles=patches, loc="upper left")
save_and_show(fig, "1_barplot_mittelwerte")

# ── 2) Boxplot – Verteilung ─────────────────────────────────────
print("2) Boxplot – Verteilung & Ausreißer")
fig, ax = plt.subplots(figsize=(12, 6))
sns.boxplot(
    data=events_no_total, x="Event", y="Zeit",
    order=order, palette=palette, ax=ax,
)
ax.set_title("Verteilung der Zeiten pro Event")
ax.set_ylabel("Sekunden")
ax.set_xlabel("")
plt.xticks(rotation=45, ha="right")
save_and_show(fig, "2_boxplot_verteilung")

# ── 3) Violin + Swarm ───────────────────────────────────────────
print("3) Violin + Swarm – Dichteform + Einzelwerte")
fig, ax = plt.subplots(figsize=(12, 6))
sns.violinplot(
    data=events_no_total, x="Event", y="Zeit",
    order=order, inner=None, palette=palette, alpha=0.4, ax=ax,
)
sns.stripplot(
    data=events_no_total, x="Event", y="Zeit",
    order=order, color="black", size=4, jitter=True, ax=ax,
)
ax.set_title("Verteilung (Violin) + Einzelmessungen")
ax.set_ylabel("Sekunden")
ax.set_xlabel("")
plt.xticks(rotation=45, ha="right")
save_and_show(fig, "3_violin_swarm")

# ── 4) Switch-only Boxplot ───────────────────────────────────────
print("4) Switch-only Boxplot")
switches = events_no_total[events_no_total["Typ"] == "Switch (Mensch)"]
sw_order = (
    switches.groupby("Event")["Zeit"]
    .mean()
    .sort_values()
    .index.tolist()
)
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(
    data=switches, x="Event", y="Zeit",
    order=sw_order, palette="Oranges", ax=ax,
)
sns.stripplot(
    data=switches, x="Event", y="Zeit",
    order=sw_order, color="black", size=4, jitter=True, ax=ax,
)
ax.set_title("Wechselzeiten (Switch) – nur menschliche Zeiten")
ax.set_ylabel("Sekunden")
ax.set_xlabel("")
plt.xticks(rotation=45, ha="right")
save_and_show(fig, "4_switch_boxplot")

# ── 5) Gestapelte Balken – Zusammensetzung pro Lauf ─────────────
print("5) Gestapelte Balken – Zusammensetzung")
# Spalten in der Reihenfolge des Barplots
cols_ordered = [c for c in order if c in df.columns]
comp = df.set_index("Lauf")[cols_ordered].fillna(0)

# Farben
bar_colors = [SWITCH_COLOR if "Switch" in c else MODULE_COLOR for c in cols_ordered]

fig, ax = plt.subplots(figsize=(10, 6))
comp.plot(
    kind="barh", stacked=True, ax=ax,
    color=bar_colors, edgecolor="white", linewidth=0.5,
)
ax.set_title("Zusammensetzung pro Lauf (gestapelt)")
ax.set_xlabel("Sekunden")
ax.set_ylabel("Lauf")
ax.legend(
    bbox_to_anchor=(1.02, 1), loc="upper left",
    fontsize=8, title="Event",
)
save_and_show(fig, "5_stacked_composition")

# ── 6) Gantt-Timeline ────────────────────────────────────────────
print("6) Gantt-Timeline – sequentielle Darstellung")
fig, ax = plt.subplots(figsize=(12, 6))
for i, lauf in enumerate(comp.index):
    left = 0
    for ev in cols_ordered:
        w = comp.loc[lauf, ev]
        if w > 0:
            color = SWITCH_COLOR if "Switch" in ev else MODULE_COLOR
            ax.barh(i, w, left=left, color=color, edgecolor="k", height=0.6, linewidth=0.3)
            # Beschriftung nur wenn breit genug
            if w > 3:
                ax.text(
                    left + w / 2, i, ev.replace("Switch_to_", "→"),
                    ha="center", va="center", fontsize=6, color="white", fontweight="bold",
                )
            left += w

ax.set_yticks(range(len(comp.index)))
ax.set_yticklabels([f"Lauf {l}" for l in comp.index])
ax.set_xlabel("Sekunden")
ax.set_title("Timeline pro Lauf (Blau = Modul, Orange = Switch)")
ax.axvline(150, color="red", linewidth=2, linestyle="--", label="150 s (Limit)")
patches = [
    mpatches.Patch(color=MODULE_COLOR, label="Modul (Roboter)"),
    mpatches.Patch(color=SWITCH_COLOR, label="Switch (Mensch)"),
]
ax.legend(handles=patches + [mpatches.Patch(color="none", label="")], loc="lower right")
save_and_show(fig, "6_gantt_timeline")

# ── 7) Korrelations-Heatmap ─────────────────────────────────────
print("7) Korrelations-Heatmap")
num_cols = [c for c in df.columns if c not in ("Lauf", "Total")]
corr = df[num_cols].corr()
fig, ax = plt.subplots(figsize=(11, 9))
sns.heatmap(
    corr, annot=True, fmt=".2f", cmap="vlag", center=0,
    square=True, linewidths=0.5, ax=ax,
)
ax.set_title("Korrelation zwischen Events")
save_and_show(fig, "7_korrelation_heatmap")

# ── 8) Total-Scatterplot – Gesamtzeit pro Lauf (ohne Verbindung) ─
print("8) Total pro Lauf (Streuplot)")
totals = df[["Lauf", "Total"]].dropna()
fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(totals["Lauf"], totals["Total"], color=MODULE_COLOR, s=100, edgecolor="black", zorder=3)
mean_total = totals["Total"].mean()
ax.axhline(mean_total, ls="--", color="gray", label=f"Ø {mean_total:.1f} s")
ax.axhline(150, ls="-", color="red", linewidth=2, label="Verfügbare Zeit: 150 s")
ax.set_title("Gesamtzeit pro Lauf (Messpunkte)")
ax.set_ylabel("Sekunden")
ax.set_xlabel("Lauf")
ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=10))
ax.grid(True, alpha=0.3)
ax.legend()
save_and_show(fig, "8_total_trend")

# ── 8b) Switch-Zeiten Entwicklung über Läufe ─────────────────────
print("8b) Switch-Zeiten Entwicklung über Läufe")
switch_cols = [c for c in df.columns if c.startswith("Switch")]
if switch_cols:
    df_switches_long = (
        df.melt(id_vars="Lauf", value_vars=switch_cols, var_name="Switch", value_name="Zeit")
        .dropna(subset=["Zeit"])
    )
    # Kürze Switch-Namen für bessere Lesbarkeit
    df_switches_long["Switch"] = df_switches_long["Switch"].str.replace("Switch_to_", "→ ", regex=False)

    fig, ax = plt.subplots(figsize=(12, 5))
    palette = sns.color_palette("tab10", len(switch_cols))
    for i, (name, group) in enumerate(df_switches_long.groupby("Switch")):
        ax.scatter(group["Lauf"], group["Zeit"], color=palette[i], s=60, edgecolor="black",
                   label=name, zorder=3, alpha=0.8)
        # Trendlinie
        if len(group) > 1:
            z = np.polyfit(group["Lauf"], group["Zeit"], 1)
            p = np.poly1d(z)
            x_line = np.linspace(group["Lauf"].min(), group["Lauf"].max(), 50)
            ax.plot(x_line, p(x_line), color=palette[i], linewidth=1.5, alpha=0.5, linestyle="--")

    ax.set_title("Switch-Zeiten Entwicklung über Läufe")
    ax.set_ylabel("Sekunden")
    ax.set_xlabel("Lauf")
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=10))
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    save_and_show(fig, "8b_switch_trend")

    # ── 8c) Einzelne Switch-Diagramme in Unterordner ─────────────
    print("8c) Einzelne Switch-Diagramme")
    SWITCH_DIR = SAVE_DIR / "switches"
    SWITCH_DIR.mkdir(exist_ok=True)
    for i, (name, group) in enumerate(df_switches_long.groupby("Switch")):
        group = group.sort_values("Lauf")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.scatter(group["Lauf"], group["Zeit"], color=SWITCH_COLOR, s=80,
                   edgecolor="black", zorder=3)
        if len(group) > 1:
            z = np.polyfit(group["Lauf"], group["Zeit"], 1)
            p = np.poly1d(z)
            x_line = np.linspace(group["Lauf"].min(), group["Lauf"].max(), 50)
            ax.plot(x_line, p(x_line), color=SWITCH_COLOR, linewidth=2, alpha=0.5, linestyle="--",
                    label=f"Trend ({z[0]:+.2f} s/Lauf)")
        mean_val = group["Zeit"].mean()
        ax.axhline(mean_val, ls="--", color="gray", alpha=0.6, label=f"Ø {mean_val:.1f} s")
        ax.set_title(f"Switch-Zeit: {name}")
        ax.set_ylabel("Sekunden")
        ax.set_xlabel("Lauf")
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=10))
        ax.grid(True, alpha=0.3)
        ax.legend()
        safe_name = name.replace("→ ", "").replace(" ", "_")
        path = SWITCH_DIR / f"switch_{safe_name}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  ✓ {path}")
        plt.close(fig)

# ══════════════════════════════════════════════════════════════════
# AUSWERTUNG LETZTER LAUF
# ══════════════════════════════════════════════════════════════════
last = df.iloc[-1]
last_nr = int(last["Lauf"])
print(f"\n── Auswertung Lauf {last_nr} ──")

# Modul- und Switch-Spalten des letzten Laufs (ohne Total, ohne Lauf)
last_events = last.drop(labels=["Lauf", "Total"], errors="ignore").dropna()
last_modules = last_events[[k for k in last_events.index if not k.startswith("Switch")]]
last_switches = last_events[[k for k in last_events.index if k.startswith("Switch")]]

# ── 9) Pie-Chart – Zeitanteile letzter Lauf ──────────────────────
print("9) Pie-Chart – Zeitanteile letzter Lauf")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Links: alle Events
colors_all = [SWITCH_COLOR if "Switch" in e else MODULE_COLOR for e in last_events.index]
wedges, texts, autotexts = axes[0].pie(
    last_events.values, labels=None, autopct="%1.1f%%",
    colors=colors_all, startangle=90, pctdistance=0.82,
    wedgeprops=dict(edgecolor="white", linewidth=1.5),
)
for t in autotexts:
    t.set_fontsize(7)
axes[0].legend(
    [e.replace("Switch_to_", "→ ") for e in last_events.index],
    loc="center left", bbox_to_anchor=(-0.35, 0.5), fontsize=8,
)
axes[0].set_title(f"Alle Events – Lauf {last_nr}")

# Rechts: nur Module
mod_colors = ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD", "#8C8C8C", "#E377C2"]
wedges2, texts2, autotexts2 = axes[1].pie(
    last_modules.values, labels=None, autopct="%1.1f%%",
    colors=mod_colors[:len(last_modules)], startangle=90, pctdistance=0.82,
    wedgeprops=dict(edgecolor="white", linewidth=1.5),
)
for t in autotexts2:
    t.set_fontsize(8)
axes[1].legend(
    last_modules.index.tolist(),
    loc="center left", bbox_to_anchor=(-0.3, 0.5), fontsize=8,
)
axes[1].set_title(f"Nur Module – Lauf {last_nr}")

fig.suptitle(f"Zeitanteile Lauf {last_nr} (Gesamt: {last['Total']:.1f} s)", fontsize=14, fontweight="bold")
save_and_show(fig, "9_pie_letzter_lauf")

# ── 10) Barplot – Zeiten letzter Lauf ────────────────────────────
print("10) Barplot – Zeiten letzter Lauf")
sorted_events = last_events.sort_values(ascending=True)
bar_cols = [SWITCH_COLOR if "Switch" in e else MODULE_COLOR for e in sorted_events.index]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(range(len(sorted_events)), sorted_events.values, color=bar_cols, edgecolor="black")
ax.set_yticks(range(len(sorted_events)))
ax.set_yticklabels([e.replace("Switch_to_", "→ ") for e in sorted_events.index])

# Werte in die Balken schreiben
for bar, val in zip(bars, sorted_events.values):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f} s", va="center", fontsize=9)

ax.set_xlabel("Sekunden")
ax.set_title(f"Zeiten pro Event – Lauf {last_nr} (Gesamt: {last['Total']:.1f} s)")
patches = [
    mpatches.Patch(color=MODULE_COLOR, label="Modul (Roboter)"),
    mpatches.Patch(color=SWITCH_COLOR, label="Switch (Mensch)"),
]
ax.legend(handles=patches, loc="lower right")
save_and_show(fig, "10_bar_letzter_lauf")

# ── 11) Modul vs. Switch – Zusammenfassung letzter Lauf ──────────
print("11) Modul vs. Switch – letzter Lauf")
mod_total = last_modules.sum()
sw_total = last_switches.sum()
rest = last["Total"] - mod_total - sw_total if not pd.isna(last.get("Total")) else 0

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Links: Vergleich Modul vs. Switch (Balken)
categories = ["Modul\n(Roboter)", "Switch\n(Mensch)"]
values = [mod_total, sw_total]
colors = [MODULE_COLOR, SWITCH_COLOR]
bars = axes[0].bar(categories, values, color=colors, edgecolor="black", width=0.5)
for bar, val in zip(bars, values):
    axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f"{val:.1f} s\n({val/last['Total']*100:.0f}%)",
                 ha="center", va="bottom", fontsize=11, fontweight="bold")
axes[0].set_ylabel("Sekunden")
axes[0].set_title(f"Roboter vs. Mensch – Lauf {last_nr}")
axes[0].set_ylim(0, max(values) * 1.25)

# Rechts: Zeitbudget (verbraucht vs. übrig)
used = last["Total"] if not pd.isna(last.get("Total")) else mod_total + sw_total
remaining = max(0, 150 - used)
over = max(0, used - 150)

if over > 0:
    budget_vals = [mod_total, sw_total, over]
    budget_labels = [f"Modul\n{mod_total:.1f}s", f"Switch\n{sw_total:.1f}s", f"Über Limit\n{over:.1f}s"]
    budget_colors = [MODULE_COLOR, SWITCH_COLOR, "#C44E52"]
else:
    budget_vals = [mod_total, sw_total, remaining]
    budget_labels = [f"Modul\n{mod_total:.1f}s", f"Switch\n{sw_total:.1f}s", f"Übrig\n{remaining:.1f}s"]
    budget_colors = [MODULE_COLOR, SWITCH_COLOR, "#55A868"]

axes[1].pie(
    budget_vals, labels=budget_labels, colors=budget_colors,
    autopct="%1.0f%%", startangle=90, pctdistance=0.75,
    wedgeprops=dict(edgecolor="white", linewidth=2),
)
axes[1].set_title(f"Zeitbudget (150 s) – Lauf {last_nr}")

fig.suptitle(f"Zusammenfassung Lauf {last_nr}", fontsize=14, fontweight="bold")
save_and_show(fig, "11_zusammenfassung_letzter_lauf")

# ══════════════════════════════════════════════════════════════════
# HEADING-DIAGRAMME
# ══════════════════════════════════════════════════════════════════
HEADING_FILE = pathlib.Path(__file__).parent.parent / "data" / "heading_data.json"

if HEADING_FILE.exists():
    with open(HEADING_FILE, "r", encoding="utf-8-sig") as f:
        heading_raw = json.load(f)

    # Normalisieren: dict → Liste mit einem Eintrag
    if isinstance(heading_raw, dict):
        heading_raw = [heading_raw]

    # segments kann {"value": [...]} statt [...] sein → entpacken
    for entry in heading_raw:
        segs = entry.get("segments", [])
        if isinstance(segs, dict):
            segs = segs.get("value", [])
            entry["segments"] = segs

        # Flat-Format (short keys m,d,h,x) → grouped segments (module, direction, distances[], headings[])
        if segs and isinstance(segs, list) and len(segs) > 0 and "m" in segs[0]:
            grouped = []
            current = None
            for pt in segs:
                m = pt.get("m", "")
                d = pt.get("d", "")
                h = pt.get("h", 0)
                x = pt.get("x", 0)
                if current is None or current["module"] != m or current["direction"] != d:
                    current = {"module": m, "direction": d, "distances": [], "headings": []}
                    grouped.append(current)
                current["distances"].append(x)
                current["headings"].append(h)
            entry["segments"] = grouped

    print("\n── Heading-Diagramme ──")

    # ── 12) Heading über Distanz – letzter Lauf ──────────────────
    print("12) Heading über Distanz – letzter Lauf")
    last_run_heading = heading_raw[-1] if heading_raw else None

    if last_run_heading and last_run_heading.get("segments"):
        segments = last_run_heading["segments"]
        run_nr = last_run_heading.get("run", "?")

        # Farbpalette pro Modul
        unique_modules = list(dict.fromkeys(s["module"] for s in segments))
        mod_palette = sns.color_palette("tab10", len(unique_modules))
        mod_color_map = dict(zip(unique_modules, mod_palette))

        fig, ax = plt.subplots(figsize=(16, 6))
        cumulative_dist = 0
        seg_boundaries = []  # Für vertikale Trennlinien zwischen Segmenten
        for i, seg in enumerate(segments):
            distances = seg["distances"]
            headings = seg["headings"]
            module = seg["module"]
            direction = seg["direction"]
            color = mod_color_map[module]
            label = f"{module} ({direction})"
            # Distanzen kumulativ verschieben, damit Segmente nacheinander erscheinen
            shifted = [d + cumulative_dist for d in distances]
            ax.scatter(shifted, headings, color=color, s=12, alpha=0.8, label=label,
                       zorder=3, edgecolors="none")
            # ±1°-Band pro Segment füllen
            if len(shifted) > 1:
                ax.fill_between(shifted, headings, 0, color=color, alpha=0.08)
            if distances:
                cumulative_dist += max(distances)
                seg_boundaries.append(cumulative_dist)

        # Vertikale Trennlinien zwischen Segmenten
        for boundary in seg_boundaries[:-1]:
            ax.axvline(boundary, color="lightgray", linewidth=0.8, linestyle=":")

        # 0°-Referenzlinie + Toleranzbänder
        ax.axhline(0, color="gray", linewidth=1, linestyle="--", alpha=0.5)
        ax.axhspan(-1, 1, color="green", alpha=0.05, label="±1° (sehr gut)")
        ax.axhspan(-3, 3, color="orange", alpha=0.03, label="±3° (akzeptabel)")

        # Deduplizierte Legende
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(),
                  bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
        ax.set_xlabel("Distanz (mm)")
        ax.set_ylabel("Heading (°)")
        ax.set_title(f"Heading über Distanz – Lauf {run_nr} (alle Fahr-Segmente)")
        ax.grid(True, alpha=0.3)
        save_and_show(fig, "12_heading_distanz_letzter_lauf")

        # ── 14) Max-Heading pro Segment – letzter Lauf ───────────
        print("14) Max-Heading pro Segment – letzter Lauf")
        seg_labels = []
        max_headings = []
        seg_colors = []
        for i, seg in enumerate(segments):
            if len(seg["headings"]) == 0:
                continue
            label = f"{seg['module']}\n({seg['direction'][:3]})"
            seg_labels.append(label)
            max_h = max(abs(h) for h in seg["headings"])
            max_headings.append(max_h)
            seg_colors.append(mod_color_map[seg["module"]])

        fig, ax = plt.subplots(figsize=(12, 5))
        bars = ax.bar(range(len(seg_labels)), max_headings,
                      color=seg_colors, edgecolor="black")
        ax.set_xticks(range(len(seg_labels)))
        ax.set_xticklabels(seg_labels, fontsize=8)
        ax.axhline(1, color="green", linewidth=1.5, linestyle="--",
                   alpha=0.7, label="1° (sehr gut)")
        ax.axhline(3, color="orange", linewidth=1.5, linestyle="--",
                   alpha=0.7, label="3° (akzeptabel)")
        ax.axhline(5, color="red", linewidth=1.5, linestyle="--",
                   alpha=0.7, label="5° (kritisch)")
        for bar, val in zip(bars, max_headings):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    f"{val:.1f}°", ha="center", va="bottom", fontsize=8)
        ax.set_ylabel("Max. Heading-Abweichung (°)")
        ax.set_xlabel("Fahr-Segment")
        ax.set_title(f"Maximale Heading-Abweichung pro Segment – Lauf {run_nr}")
        ax.legend(loc="upper right")
        save_and_show(fig, "14_max_heading_letzter_lauf")
    else:
        print("  ! Kein Heading-Daten im letzten Lauf")

    # ── 13) Heading-Abweichung pro Modul – Boxplot alle Läufe ────
    print("13) Heading-Abweichung pro Modul – alle Läufe")
    all_heading_rows = []
    for run_entry in heading_raw:
        run_nr = run_entry.get("run", 0)
        for seg in run_entry.get("segments", []):
            module = seg["module"]
            direction = seg["direction"]
            for h in seg["headings"]:
                all_heading_rows.append({
                    "Lauf": run_nr,
                    "Modul": module,
                    "Richtung": direction,
                    "Heading": abs(h),
                })

    if all_heading_rows:
        df_heading = pd.DataFrame(all_heading_rows)
        mod_order = (
            df_heading.groupby("Modul")["Heading"]
            .median()
            .sort_values()
            .index.tolist()
        )

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(
            data=df_heading, x="Modul", y="Heading",
            order=mod_order, ax=ax, palette="tab10",
        )
        ax.axhline(1, color="green", linewidth=1.5, linestyle="--",
                   alpha=0.7, label="1° (sehr gut)")
        ax.axhline(3, color="orange", linewidth=1.5, linestyle="--",
                   alpha=0.7, label="3° (akzeptabel)")
        ax.set_ylabel("Heading-Abweichung |°|")
        ax.set_xlabel("")
        ax.set_title("Heading-Abweichung pro Modul (alle Läufe)")
        ax.legend(loc="upper right")
        plt.xticks(rotation=45, ha="right")
        save_and_show(fig, "13_heading_boxplot_alle_laeufe")
    else:
        print("  ! Keine Heading-Daten vorhanden")
else:
    print("\n⚠ heading_data.json nicht gefunden – Heading-Plots übersprungen")
    print("  (Heading-Daten werden beim nächsten Roboter-Lauf erfasst)")

print(f"\n✅ Alle Plots gespeichert in: {SAVE_DIR.resolve()}")
