import matplotlib.pyplot as plt
import json

def plot_positions(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    x = [pos['x'] for pos in data]
    y = [pos['y'] for pos in data]
    # Note: map image is deleted, showing plot without background
    fig, ax = plt.subplots()
    plt.plot(x, y)
    plt.title('Robot Position Plot')
    plt.xlabel('X Position (cm)')
    plt.ylabel('Y Position (cm)')
    plt.grid(True)
    plt.axis('equal')
    plt.show()

if __name__ == "__main__":
    plot_positions('../../data/positionen.json')
