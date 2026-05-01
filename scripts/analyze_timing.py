import csv
import numpy as np
import pandas as pd
import plotly.express as px

KEY_BYTE = 0x01

rows = []

with open("timing_big.csv") as f:
    lines = [line for line in f if not line.startswith("#")]
    reader = csv.DictReader(lines)

    for row in reader:
        val = int(row["val"])
        rows.append({
            "val": val,
            "idx": val ^ KEY_BYTE,
            "sample": int(row["sample"]),
            "ticks": int(row["ticks"]),
        })

df = pd.DataFrame(rows)

summary = (
    df.groupby(["val", "idx"])["ticks"]
      .agg(["mean", "median", "std", "count"])
      .reset_index()
)

summary["mean_centered"] = summary["mean"] - summary["mean"].mean()

fig = px.scatter(
    summary,
    x="idx",
    y="mean_centered",
    hover_data={
        "val": True,
        "idx": True,
        "mean": ":.2f",
        "median": ":.2f",
        "std": ":.2f",
        "count": True,
        "mean_centered": ":.2f",
    },
    title="Mean timing by AES first-round index: plaintext byte XOR key byte",
    labels={
        "idx": "Intermediate index = plaintext byte XOR key byte",
        "mean_centered": "Mean ticks minus global mean",
    },
)

fig.add_hline(y=0)
fig.show()