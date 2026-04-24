#!/usr/bin/env python3

import os
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

RESULT_DIR = "results_corun"
OUT_DIR = "analysis_corun"

os.makedirs(OUT_DIR, exist_ok=True)

def load_timings(path):
    vals = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Handles plain logs like: 1234
            # Also handles lines containing extra text/numbers.
            nums = re.findall(r"\d+", line)
            if nums:
                vals.append(int(nums[-1]))

    return np.array(vals, dtype=np.int64)

def summarize(vals):
    return {
        "n": len(vals),
        "mean": np.mean(vals),
        "median": np.median(vals),
        "std": np.std(vals),
        "min": np.min(vals),
        "p90": np.percentile(vals, 90),
        "p95": np.percentile(vals, 95),
        "p99": np.percentile(vals, 99),
        "max": np.max(vals),
    }

def parse_name(path):
    name = os.path.basename(path)

    if "_alone" in name:
        impl = name.split("_alone")[0]
        load = 0
    else:
        m = re.match(r"(ct|big)_load_(\d+)\.log", name)
        if not m:
            return None
        impl = m.group(1)
        load = int(m.group(2))

    return impl, load

rows = []

for path in glob.glob(os.path.join(RESULT_DIR, "*.log")):
    parsed = parse_name(path)
    if parsed is None:
        continue

    impl, load = parsed
    vals = load_timings(path)

    if len(vals) == 0:
        print(f"Skipping empty file: {path}")
        continue

    stats = summarize(vals)
    stats["impl"] = impl
    stats["load"] = load
    stats["path"] = path
    rows.append(stats)

if not rows:
    print("No result logs found.")
    exit(1)

rows.sort(key=lambda r: (r["load"], r["impl"]))

# Print summary table
print()
print(f"{'impl':<6} {'load':>8} {'n':>8} {'mean':>12} {'median':>12} {'std':>12} {'p95':>12} {'p99':>12} {'max':>12}")
print("-" * 100)

for r in rows:
    print(
        f"{r['impl']:<6} "
        f"{r['load']:>8} "
        f"{r['n']:>8} "
        f"{r['mean']:>12.2f} "
        f"{r['median']:>12.2f} "
        f"{r['std']:>12.2f} "
        f"{r['p95']:>12.2f} "
        f"{r['p99']:>12.2f} "
        f"{r['max']:>12.2f}"
    )

# Save CSV
csv_path = os.path.join(OUT_DIR, "summary.csv")
with open(csv_path, "w") as f:
    f.write("impl,load,n,mean,median,std,min,p90,p95,p99,max,path\n")
    for r in rows:
        f.write(
            f"{r['impl']},{r['load']},{r['n']},"
            f"{r['mean']},{r['median']},{r['std']},"
            f"{r['min']},{r['p90']},{r['p95']},{r['p99']},{r['max']},"
            f"{r['path']}\n"
        )

print(f"\nSaved summary to {csv_path}")

# Group data
loads = sorted(set(r["load"] for r in rows))
impls = ["ct", "big"]

def get_stat(impl, load, stat):
    for r in rows:
        if r["impl"] == impl and r["load"] == load:
            return r[stat]
    return np.nan

# Plot median latency vs load
plt.figure()
for impl in impls:
    y = [get_stat(impl, load, "median") for load in loads]
    plt.plot(loads, y, marker="o", label=impl)

plt.xlabel("Co-runner load")
plt.ylabel("Median cycles / ticks")
plt.title("Median AES Timing vs Co-runner Load")
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(OUT_DIR, "median_vs_load.png"), dpi=200)
plt.close()

# Plot p95 latency vs load
plt.figure()
for impl in impls:
    y = [get_stat(impl, load, "p95") for load in loads]
    plt.plot(loads, y, marker="o", label=impl)

plt.xlabel("Co-runner load")
plt.ylabel("p95 cycles / ticks")
plt.title("p95 AES Timing vs Co-runner Load")
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(OUT_DIR, "p95_vs_load.png"), dpi=200)
plt.close()

# Plot p99 latency vs load
plt.figure()
for impl in impls:
    y = [get_stat(impl, load, "p99") for load in loads]
    plt.plot(loads, y, marker="o", label=impl)

plt.xlabel("Co-runner load")
plt.ylabel("p99 cycles / ticks")
plt.title("p99 AES Timing vs Co-runner Load")
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(OUT_DIR, "p99_vs_load.png"), dpi=200)
plt.close()

# Plot jitter/std vs load
plt.figure()
for impl in impls:
    y = [get_stat(impl, load, "std") for load in loads]
    plt.plot(loads, y, marker="o", label=impl)

plt.xlabel("Co-runner load")
plt.ylabel("Standard deviation")
plt.title("Timing Variability vs Co-runner Load")
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(OUT_DIR, "std_vs_load.png"), dpi=200)
plt.close()

# Deadline miss style plots
# Uses baseline p99 of each implementation alone as an artificial deadline.
for impl in impls:
    baseline = get_stat(impl, 0, "p99")
    if np.isnan(baseline):
        continue

    miss_rates = []

    for load in loads:
        path = None
        for r in rows:
            if r["impl"] == impl and r["load"] == load:
                path = r["path"]
                break

        if path is None:
            miss_rates.append(np.nan)
            continue

        vals = load_timings(path)
        miss_rate = np.mean(vals > baseline) * 100.0
        miss_rates.append(miss_rate)

    plt.figure()
    plt.plot(loads, miss_rates, marker="o")
    plt.xlabel("Co-runner load")
    plt.ylabel("Miss rate (%)")
    plt.title(f"{impl} Deadline Miss Rate vs Load\nDeadline = alone p99 = {baseline:.2f}")
    plt.grid(True)
    plt.savefig(os.path.join(OUT_DIR, f"{impl}_miss_rate_vs_load.png"), dpi=200)
    plt.close()

# Distribution plots for each load
for load in loads:
    plt.figure()

    for impl in impls:
        path = None
        for r in rows:
            if r["impl"] == impl and r["load"] == load:
                path = r["path"]
                break

        if path is None:
            continue

        vals = load_timings(path)

        # Clip extreme outliers for readability only
        lo = np.percentile(vals, 1)
        hi = np.percentile(vals, 99)
        clipped = vals[(vals >= lo) & (vals <= hi)]

        plt.hist(clipped, bins=80, alpha=0.5, density=True, label=impl)

    label = "alone" if load == 0 else f"load {load}"
    plt.xlabel("Cycles / ticks")
    plt.ylabel("Density")
    plt.title(f"Timing Distribution: {label}")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(OUT_DIR, f"distribution_load_{load}.png"), dpi=200)
    plt.close()

print(f"Saved plots to {OUT_DIR}/")
