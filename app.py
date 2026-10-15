"""Web page for the coffee shop simulator.

Every page load runs one fresh simulated morning and shows how many
customers were served, their average wait, and a chart of each
customer's wait by arrival time.

Run with:  flask --app app run
"""

import base64
import io

import numpy as np
from flask import Flask, render_template_string
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MultipleLocator

from coffee import OPEN_MINUTES, simulate_morning

app = Flask(__name__)

OPENING_HOUR = 7

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Coffee Shop Morning</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #f9f9f7; color: #0b0b0b;
           max-width: 52rem; margin: 2rem auto; padding: 0 16px; }
    h1 { font-size: 1.5rem; margin-bottom: .25rem; }
    .sub { color: #52514e; margin-top: 0; }
    .stats { display: flex; gap: 1rem; flex-wrap: wrap; margin: 1.5rem 0; }
    .stat { background: #fcfcfb; border: 1px solid rgba(11,11,11,.10);
            border-radius: 8px; padding: 1rem 1.25rem; min-width: 10rem; }
    .stat .label { color: #52514e; font-size: .875rem; }
    .stat .value { font-size: 2rem; font-weight: 600; }
    img { width: 100%; height: auto; border: 1px solid rgba(11,11,11,.10); border-radius: 8px; }
  </style>
</head>
<body>
  <h1>One morning at the coffee shop</h1>
  <p class="sub">7:00&ndash;11:00, one barista. Reload the page to simulate another morning.</p>
  <div class="stats">
    <div class="stat"><div class="label">Customers served</div>
      <div class="value">{{ served }}</div></div>
    <div class="stat"><div class="label">Average wait</div>
      <div class="value">{{ average }}</div></div>
  </div>
  {% if chart %}
  <img src="data:image/png;base64,{{ chart }}"
       alt="Wait in minutes for each customer, by the time they arrived">
  {% endif %}
</body>
</html>
"""


def clock(minutes, _pos=None):
    """Format minutes after opening as a clock time, e.g. 95 -> '8:35'."""
    hours, mins = divmod(int(round(minutes)), 60)
    return f"{OPENING_HOUR + hours}:{mins:02d}"


def wait_chart(arrivals, waits):
    """Return a PNG of each customer's wait by arrival time, base64-encoded."""
    # Use Figure directly rather than pyplot, which isn't safe across
    # Flask's request threads.
    fig = Figure(figsize=(8, 3.6), dpi=150, facecolor="#fcfcfb")
    ax = fig.add_subplot()
    ax.set_facecolor("#fcfcfb")

    ax.plot(arrivals, waits, color="#2a78d6", linewidth=1.5,
            marker="o", markersize=3.5)

    ax.set_xlim(0, OPEN_MINUTES)
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_locator(MultipleLocator(30))
    ax.xaxis.set_major_formatter(FuncFormatter(clock))
    ax.set_xlabel("Arrival time", color="#52514e")
    ax.set_ylabel("Wait (minutes)", color="#52514e")
    ax.set_title("Each customer's wait", loc="left", color="#0b0b0b")

    ax.grid(axis="y", color="#e1e0d9", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors="#898781", length=0)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    return base64.b64encode(buf.getvalue()).decode("ascii")


@app.route("/")
def index():
    arrivals, waits = simulate_morning(np.random.default_rng())
    return render_template_string(
        PAGE,
        served=waits.size,
        average=f"{waits.mean():.2f} min" if waits.size else "—",
        chart=wait_chart(arrivals, waits) if waits.size else None,
    )


if __name__ == "__main__":
    app.run(debug=True)
