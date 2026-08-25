"""
Timing Diagram Visualization
This program reads the timing data from timing_data.json and creates diagrams.
"""

import json
import matplotlib.pyplot as plt
from datetime import datetime

def load_timing_data():
    """Load timing data from JSON file."""
    try:
        with open("../../data/timing_data.json", "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: ../../data/timing_data.json not found. Run main.py first to collect data.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: ../../data/timing_data.json is corrupted. Details: {e}")
        return None
    except Exception as e:
        print(f"Error loading ../../data/timing_data.json: {e}")
        return None

def plot_bar_chart(data):
    """Create a bar chart showing the latest run's timing data."""
    if not data:
        return
    
    # Handle both list (multiple runs) and dict (single run) formats
    if isinstance(data, list):
        latest_run = data[-1]
    else:
        latest_run = data
    
    # Filter out non-task entries
    tasks = {k: v for k, v in latest_run.items() if k not in ["Total"]}

    # Determine total time: prefer explicit 'Total' field if present
    total_time = latest_run.get("Total", sum(tasks.values()))

    plt.figure(figsize=(12, 6))

    # Color mapping that handles both old and new naming conventions
    def get_color(task_name):
        task_lower = task_name.lower()
        if 'green' in task_lower:
            return 'lightgreen' if 'switch' in task_lower or 'to' in task_lower else 'green'
        elif 'red' in task_lower:
            return 'lightcoral' if 'switch' in task_lower or 'to' in task_lower else 'red'
        elif 'blue' in task_lower:
            return 'lightblue' if 'switch' in task_lower or 'to' in task_lower else 'blue'
        elif 'yellow' in task_lower:
            return 'lightyellow' if 'switch' in task_lower or 'to' in task_lower else 'gold'
        elif 'colourless' in task_lower:
            return 'lightgray' if 'switch' in task_lower or 'to' in task_lower else 'gray'
        return 'gray'
    
    bar_colors = [get_color(task) for task in tasks.keys()]

    bars = plt.bar(tasks.keys(), tasks.values(), color=bar_colors, edgecolor='black')
    
    plt.xlabel('Task')
    plt.ylabel('Time (seconds)')
    plt.title('Task Timing')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, value in zip(bars, tasks.values()):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                 f'{value:.2f}s', ha='center', va='bottom', fontweight='bold', fontsize=8)

    # Display total time above the chart
    plt.gca().text(0.5, 1.05, f'Total Time: {total_time:.2f}s', transform=plt.gca().transAxes,
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../timing_bar_chart.png', dpi=150)
    plt.show()
    print("Bar chart saved as ../timing_bar_chart.png")

def plot_history(data):
    """Create a line chart showing timing history over multiple runs."""
    if not data:
        print("No data available for history chart.")
        return
    
    # If data is a dict (single run), can't create history
    if isinstance(data, dict):
        print("History chart requires multiple runs. Only one run available.")
        return
    
    if len(data) < 2:
        print("Not enough data for history chart (need at least 2 runs).")
        return
    
    # Collect all unique tasks
    all_tasks = set()
    for run in data:
        for key in run.keys():
            if key not in ["Total"]:
                all_tasks.add(key)
    
    plt.figure(figsize=(14, 7))
    
    # Color mapping function for history chart
    def get_task_color(task_name):
        task_lower = task_name.lower()
        if 'green' in task_lower:
            return 'lightgreen' if 'switch' in task_lower or 'to' in task_lower else 'green'
        elif 'red' in task_lower:
            return 'lightcoral' if 'switch' in task_lower or 'to' in task_lower else 'red'
        elif 'blue' in task_lower:
            return 'lightblue' if 'switch' in task_lower or 'to' in task_lower else 'blue'
        elif 'yellow' in task_lower:
            return 'lightyellow' if 'switch' in task_lower or 'to' in task_lower else 'gold'
        elif 'colourless' in task_lower:
            return 'lightgray' if 'switch' in task_lower or 'to' in task_lower else 'gray'
        return 'gray'
    
    # Plot each task
    for task in all_tasks:
        times = [run.get(task, 0) for run in data]
        run_numbers = list(range(1, len(data) + 1))
        plt.plot(run_numbers, times, marker='o', label=task, 
                 color=get_task_color(task), linewidth=2, markersize=8)
    
    # Plot total time
    total_times = [run.get("Total", 0) for run in data]
    plt.plot(run_numbers, total_times, marker='s', label='Total', 
             color='purple', linewidth=2, markersize=8, linestyle='--')
    
    plt.xlabel('Run Number')
    plt.ylabel('Time (seconds)')
    plt.title('Timing History Across Runs')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(run_numbers)
    
    plt.tight_layout()
    plt.savefig('../timing_history.png', dpi=150)
    plt.show()
    print("History chart saved as ../timing_history.png")

def plot_pie_chart(data):
    """Create a pie chart showing time distribution for the latest run."""
    if not data:
        return
    
    # Handle both list (multiple runs) and dict (single run) formats
    if isinstance(data, list):
        latest_run = data[-1]
    else:
        latest_run = data
    
    # Filter out non-task entries
    tasks = {k: v for k, v in latest_run.items() if k not in ["Total"]}
    
    if not tasks:
        print("No task data available for pie chart.")
        return
    
    plt.figure(figsize=(10, 10))
    
    # Color mapping for pie chart
    def get_pie_color(task_name):
        task_lower = task_name.lower()
        if 'green' in task_lower:
            return 'lightgreen' if 'switch' in task_lower or 'to' in task_lower else 'green'
        elif 'red' in task_lower:
            return 'lightcoral' if 'switch' in task_lower or 'to' in task_lower else 'red'
        elif 'blue' in task_lower:
            return 'lightblue' if 'switch' in task_lower or 'to' in task_lower else 'blue'
        elif 'yellow' in task_lower:
            return 'lightyellow' if 'switch' in task_lower or 'to' in task_lower else 'gold'
        elif 'colourless' in task_lower:
            return 'lightgray' if 'switch' in task_lower or 'to' in task_lower else 'gray'
        return 'gray'
    
    pie_colors = [get_pie_color(task) for task in tasks.keys()]
    
    plt.pie(tasks.values(), labels=tasks.keys(), colors=pie_colors,
            autopct='%1.1f%%', startangle=90, explode=[0.02]*len(tasks))
    
    plt.title('Time Distribution')
    
    plt.tight_layout()
    plt.savefig('../timing_pie_chart.png', dpi=150)
    plt.show()
    print("Pie chart saved as ../timing_pie_chart.png")

def main():
    """Main function to run the visualization."""
    print("=" * 50)
    print("Timing Data Visualization")
    print("=" * 50)
    
    data = load_timing_data()
    if not data:
        return
    
    # Display correct information based on data structure
    if isinstance(data, dict):
        print("\nFound 1 run in the data.\n")
    else:
        print(f"\nFound {len(data)} run(s) in the data.\n")
    
    print("Choose a diagram type:")
    print("1. Bar Chart (latest run)")
    print("2. History Line Chart (all runs)")
    print("3. Pie Chart (latest run)")
    print("4. All diagrams")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == '1':
        plot_bar_chart(data)
    elif choice == '2':
        plot_history(data)
    elif choice == '3':
        plot_pie_chart(data)
    elif choice == '4':
        plot_bar_chart(data)
        plot_history(data)
        plot_pie_chart(data)
    else:
        print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
