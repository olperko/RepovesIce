import analyzer
import config
import matplotlib.pyplot as plt


def main():
    print("Starting Repovesi Ice Analysis...")
    print(f"Time window: {config.TIME_WINDOW}")
    print(f"Cloud cover limit: {config.CLOUD_COVER_LIMIT}%")
    print(f"NDSI threshold: {config.ICE_THRESHOLD_NDSI}")
    print(f"NDWI threshold: {config.ICE_THRESHOLD_NDWI}")
    print()

    # Run the data collection
    results = analyzer.run_full_analysis()

    if not results:
        print("No data found.")
        return

    # Print Summary Report
    print("\n" + "="*60)
    print("SEASONAL MELT REPORT".center(60))
    print("="*60)

    for entry in sorted(results, key=lambda x: x['date']):
        ice_pct = entry['ice_pct']

        if ice_pct > config.STATUS_FROZEN_THRESHOLD:
            status = "FROZEN"
        elif ice_pct < config.STATUS_OPEN_THRESHOLD:
            status = "OPEN"
        else:
            status = "SLUSH"

        print(f"{entry['date']}: {ice_pct:5.1f}% ice coverage - {status}")

    print("="*60 + "\n")

    # Create visualizations
    create_visualizations(results)


def create_visualizations(results):
    """
    Plot ice coverage over the season: the single number that answers the
    project's actual question (when is the route clear?), instead of
    overlaying a route-distance profile line for every date.
    """
    sorted_results = sorted(results, key=lambda x: x['date'])
    dates = [entry['date'] for entry in sorted_results]
    ice_pcts = [entry['ice_pct'] for entry in sorted_results]

    status_colors = []
    for pct in ice_pcts:
        if pct > config.STATUS_FROZEN_THRESHOLD:
            status_colors.append('#4A90D9')  # frozen - blue
        elif pct < config.STATUS_OPEN_THRESHOLD:
            status_colors.append('#4CAF50')  # open - green
        else:
            status_colors.append('#FFA726')  # slush - orange

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(dates, ice_pcts, color='gray', linewidth=1.5, zorder=1)
    ax.scatter(dates, ice_pcts, c=status_colors, s=60, zorder=2, edgecolors='white')

    ax.axhline(y=config.STATUS_FROZEN_THRESHOLD, color='#4A90D9', linestyle='--',
               alpha=0.6, label=f'Frozen threshold ({config.STATUS_FROZEN_THRESHOLD}%)')
    ax.axhline(y=config.STATUS_OPEN_THRESHOLD, color='#4CAF50', linestyle='--',
               alpha=0.6, label=f'Open threshold ({config.STATUS_OPEN_THRESHOLD}%)')

    ax.set_title("Repovesi Route: Ice Coverage Over the Season", fontsize=13, fontweight='bold')
    ax.set_xlabel("Date")
    ax.set_ylabel("Ice coverage (%)")
    ax.set_ylim(-5, 105)
    ax.legend(loc='center left')
    ax.grid(True, alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    plt.tight_layout()

    # Save the figure
    output_file = "repovesi_melt_report.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Visualization saved to: {output_file}")

    plt.show()


if __name__ == "__main__":
    main()
