"""Simulate one morning (7:00-11:00) at a coffee shop with one barista.

Customers arrive at random (a Poisson process, about one every three
minutes) and each order takes between one and four minutes to make.
The door closes at 11:00, but anyone already in line is still served.
A customer's wait is the time from arriving until the barista starts
their order.
"""

import sys

import numpy as np

OPEN_MINUTES = 4 * 60      # 7:00 to 11:00
MEAN_ARRIVAL_GAP = 3.0     # minutes between customers, on average
MIN_ORDER, MAX_ORDER = 1.0, 4.0  # minutes to make one order


def simulate(rng):
    """Return the wait, in minutes, of every customer served this morning."""
    # Draw more gaps than we could plausibly need, then keep only the
    # customers who arrive before closing.
    gaps = rng.exponential(MEAN_ARRIVAL_GAP, size=int(OPEN_MINUTES / MEAN_ARRIVAL_GAP * 3))
    arrivals = np.cumsum(gaps)
    arrivals = arrivals[arrivals < OPEN_MINUTES]

    order_times = rng.uniform(MIN_ORDER, MAX_ORDER, size=arrivals.size)

    waits = np.empty(arrivals.size)
    barista_free_at = 0.0
    for i, arrival in enumerate(arrivals):
        start = max(arrival, barista_free_at)
        waits[i] = start - arrival
        barista_free_at = start + order_times[i]
    return waits


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    waits = simulate(np.random.default_rng(seed))

    print(f"Customers served: {waits.size}")
    if waits.size:
        print(f"Average wait: {waits.mean():.2f} minutes")


if __name__ == "__main__":
    main()
