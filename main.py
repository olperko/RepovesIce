import analyzer
import matplotlib.pyplot as plt
import numpy as np


def main():
    print("🚀 Starting Repovesi Ice Analysis...")

    # Run the data collection
    results = analyzer.run_full_analysis()

    if not results:
        print("❌ No data found.")
        return

    # Print Summary Report
    print("\n--- SEASONAL MELT REPORT ---")
    for entry in sorted(results, key=lambda x: x['date']):
        status = "🧊 FROZEN" if entry['ice_pct'] > 50 else "🚤 OPEN" if entry['ice_pct'] < 10 else "⚠️ SLUSH"
        print(f"{entry['date']}: {entry['ice_pct']:5.1f}% ice coverage - {status}")

    # Create the Visualization
    plt.figure(figsize=(12, 6))
    for entry in sorted(results, key=lambda x: x['date']):
        plt.plot(np.array(entry['distances']) / 1000, entry['profile'], label=entry['date'])

    plt.axhline(y=0.4, color='red', linestyle='--', label='Ice Threshold')
    plt.title("Repovesi Route Melt Profile")
    plt.xlabel("KM from Start")
    plt.ylabel("Ice Intensity (NDSI)")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()