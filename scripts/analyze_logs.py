#!/usr/bin/env python

import argparse
import pathlib
import re

import pandas as pd
import matplotlib.pyplot as plt


ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG_ROOT = ROOT / "logs"


def latest_log_dir():
    dirs = [p for p in LOG_ROOT.iterdir() if p.is_dir()]
    if not dirs:
        raise RuntimeError("No log directories found")
    return max(dirs, key=lambda p: p.stat().st_mtime)


def parse_metadata(path):
    metadata = {}

    with open(path) as f:
        first = f.readline().strip()

    if first.startswith("#"):
        for part in first[1:].strip().split():
            if "=" in part:
                k, v = part.split("=", 1)
                metadata[k] = v

    # fallback from filename: ct_buf16_cache1.log
    m = re.search(r"(ct|big)_buf(\d+)_cache(\d+)", path.name)
    if m:
        metadata.setdefault("impl", m.group(1))
        metadata.setdefault("buf", m.group(2))
        metadata.setdefault("cache", m.group(3))

    return metadata


def load_logs(log_dir):
    frames = []

    for path in sorted(log_dir.glob("*.log")):
        meta = parse_metadata(path)

        df = pd.read_csv(path, comment="#")
        df["impl"] = meta.get("impl", "unknown")
        df["buf"] = int(meta.get("buf", 0))
        df["cache"] = int(meta.get("cache", 0))
        df["source"] = path.name

        frames.append(df)

    if not frames:
        raise RuntimeError(f"No .log files found in {log_dir}")

    return pd.concat(frames, ignore_index=True)


def add_trimmed_columns(df):
    groups = []

    for _, g in df.groupby(["impl", "buf", "cache"]):
        lo = g["ticks"].quantile(0.01)
        hi = g["ticks"].quantile(0.99)

        g = g.copy()
        g["ticks_clipped"] = g["ticks"].clip(lo, hi)
        g["is_outlier_1_99"] = (g["ticks"] < lo) | (g["ticks"] > hi)

        groups.append(g)

    return pd.concat(groups, ignore_index=True)


def summarize(df, out_dir):
    summary = (
        df.groupby(["impl", "buf", "cache"])
        .agg(
            count=("ticks", "count"),
            mean=("ticks", "mean"),
            median=("ticks", "median"),
            std=("ticks", "std"),
            min=("ticks", "min"),
            max=("ticks", "max"),
            p01=("ticks", lambda x: x.quantile(0.01)),
            p05=("ticks", lambda x: x.quantile(0.05)),
            p95=("ticks", lambda x: x.quantile(0.95)),
            p99=("ticks", lambda x: x.quantile(0.99)),
            clipped_mean=("ticks_clipped", "mean"),
            clipped_std=("ticks_clipped", "std"),
            outlier_count=("is_outlier_1_99", "sum"),
        )
        .reset_index()
    )

    path = out_dir / "analysis_summary.csv"
    summary.to_csv(path, index=False)

    print(summary.to_string(index=False))
    print(f"\n[+] Wrote {path}")

    return summary


def plot_median_by_buffer(summary, out_dir):
    plt.figure()

    for impl in sorted(summary["impl"].unique()):
        for cache in sorted(summary["cache"].unique()):
            s = summary[(summary["impl"] == impl) & (summary["cache"] == cache)]
            label = f"{impl}, cache={cache}"
            plt.plot(s["buf"], s["median"], marker="o", label=label)

    plt.xscale("log", base=2)
    plt.xlabel("buffer size")
    plt.ylabel("median ticks")
    plt.title("Median timing by buffer size")
    plt.legend()
    plt.grid(True, which="both")

    out = out_dir / "median_by_buffer.png"
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[+] Wrote {out}")


def plot_cache_penalty(summary, out_dir):
    rows = []

    for impl in sorted(summary["impl"].unique()):
        for buf in sorted(summary["buf"].unique()):
            no = summary[(summary["impl"] == impl) & (summary["buf"] == buf) & (summary["cache"] == 0)]
            yes = summary[(summary["impl"] == impl) & (summary["buf"] == buf) & (summary["cache"] == 1)]

            if no.empty or yes.empty:
                continue

            no_med = float(no["median"].iloc[0])
            yes_med = float(yes["median"].iloc[0])

            rows.append({
                "impl": impl,
                "buf": buf,
                "cache_penalty_ticks": yes_med - no_med,
                "cache_penalty_pct": ((yes_med - no_med) / no_med) * 100.0,
            })

    penalty = pd.DataFrame(rows)
    penalty.to_csv(out_dir / "cache_penalty.csv", index=False)

    plt.figure()

    for impl in sorted(penalty["impl"].unique()):
        s = penalty[penalty["impl"] == impl]
        plt.plot(s["buf"], s["cache_penalty_pct"], marker="o", label=impl)

    plt.xscale("log", base=2)
    plt.xlabel("buffer size")
    plt.ylabel("cache penalty (%)")
    plt.title("Median cache-eviction penalty")
    plt.legend()
    plt.grid(True, which="both")

    out = out_dir / "cache_penalty_pct.png"
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[+] Wrote {out}")


def plot_distributions(df, out_dir):
    for buf in sorted(df["buf"].unique()):
        plt.figure()

        subset = df[df["buf"] == buf]

        for impl in sorted(subset["impl"].unique()):
            for cache in sorted(subset["cache"].unique()):
                s = subset[(subset["impl"] == impl) & (subset["cache"] == cache)]
                label = f"{impl}, cache={cache}"
                plt.hist(
                    s["ticks_clipped"],
                    bins=80,
                    density=True,
                    alpha=0.35,
                    label=label,
                )

        plt.xlabel("ticks, clipped 1–99%")
        plt.ylabel("density")
        plt.title(f"Timing distribution, buf={buf}")
        plt.legend()

        out = out_dir / f"distribution_buf{buf}.png"
        plt.savefig(out, dpi=200, bbox_inches="tight")
        plt.close()
        print(f"[+] Wrote {out}")


def plot_variability(summary, out_dir):
    plt.figure()

    for impl in sorted(summary["impl"].unique()):
        for cache in sorted(summary["cache"].unique()):
            s = summary[(summary["impl"] == impl) & (summary["cache"] == cache)].copy()
            s["cv"] = s["clipped_std"] / s["clipped_mean"]
            label = f"{impl}, cache={cache}"
            plt.plot(s["buf"], s["cv"], marker="o", label=label)

    plt.xscale("log", base=2)
    plt.xlabel("buffer size")
    plt.ylabel("coefficient of variation")
    plt.title("Relative timing variability, clipped 1–99%")
    plt.legend()
    plt.grid(True, which="both")

    out = out_dir / "variability_cv.png"
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[+] Wrote {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log-dir",
        type=pathlib.Path,
        default=None,
        help="Specific logs/<timestamp> directory to analyze",
    )
    args = parser.parse_args()

    log_dir = args.log_dir if args.log_dir else latest_log_dir()
    out_dir = log_dir / "analysis"
    out_dir.mkdir(exist_ok=True)

    print(f"[*] Analyzing {log_dir}")

    df = load_logs(log_dir)
    df = add_trimmed_columns(df)

    summary = summarize(df, out_dir)

    plot_median_by_buffer(summary, out_dir)
    plot_cache_penalty(summary, out_dir)
    plot_distributions(df, out_dir)
    plot_variability(summary, out_dir)

    print(f"\n[+] Analysis written to {out_dir}")


if __name__ == "__main__":
    main()
