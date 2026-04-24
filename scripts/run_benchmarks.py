#!/usr/bin/env python

import subprocess
import pathlib
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIN = ROOT / "build/aes_bench"
LOG_ROOT = ROOT / "logs"

RUNS = 10000
BUF_SIZES = [16, 64, 256, 1024]
IMPLS = ["ct", "big"]
CACHE_MODES = [0, 1]


def is_raspberry_pi():
    model_path = "/proc/device-tree/model"
    
    if os.path.exists(model_path):
        with open(model_path, 'r', errors="ignore") as f:
            model = f.read().lower()
            return "raspberry pi" in model
    
    return False

def run_cmd(cmd, logfile):
    print(f"[*] Running: {' '.join(map(str, cmd))}")

    with open(logfile, "w") as f:
        subprocess.run(
            cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            check=True,
            cwd=ROOT,
        )


def run_benchmarks(outdir):
    for impl in IMPLS:
        for buf in BUF_SIZES:
            for cache in CACHE_MODES:
                logfile = outdir / f"{impl}_buf{buf}_cache{cache}.log"

                base_cmd = [
                    str(BIN),
                    "--impl", impl,
                    "--sz", str(buf),
                    "--n", str(RUNS),
                    "--cache", str(cache),
                ]
                
                if is_raspberry_pi():
                    cmd = ["taskset", "-c", "3"] + base_cmd
                else:
                    cmd = base_cmd
                    
                    
                run_cmd(cmd, logfile)


def read_log(path):
    metadata = {}

    with open(path) as f:
        first = f.readline().strip()

    if first.startswith("#"):
        parts = first[1:].strip().split()
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                metadata[k] = v

    df = pd.read_csv(path, comment="#")
    df["impl"] = metadata.get("impl", "unknown")
    df["buf"] = int(metadata.get("buf", 0))
    df["runs"] = int(metadata.get("runs", 0))
    df["cache"] = int(metadata.get("cache", 0))
    df["source"] = path.name

    return df


def load_logs(outdir):
    frames = []

    for path in sorted(outdir.glob("*.log")):
        frames.append(read_log(path))

    if not frames:
        raise RuntimeError(f"No logs found in {outdir}")

    return pd.concat(frames, ignore_index=True)


def summarize(df, outdir):
    summary = (
        df.groupby(["impl", "buf", "cache"])["ticks"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )

    summary_path = outdir / "summary.csv"
    summary.to_csv(summary_path, index=False)

    print("\n[+] Summary:")
    print(summary.to_string(index=False))
    print(f"\n[+] Wrote {summary_path}")

    return summary


def plot_distributions(df, outdir):
    for buf in sorted(df["buf"].unique()):
        for cache in sorted(df["cache"].unique()):
            subset = df[(df["buf"] == buf) & (df["cache"] == cache)]

            if subset.empty:
                continue

            plt.figure()

            for impl in sorted(subset["impl"].unique()):
                vals = subset[subset["impl"] == impl]["ticks"]
                vals = vals.clip(
                    lower=vals.quantile(0.05),
                    upper=vals.quantile(0.95),
                )

                plt.hist(vals, bins=80, alpha=0.5, density=True, label=impl)

            plt.title(f"AES timing distribution: buf={buf}, cache={cache}")
            plt.xlabel("ticks")
            plt.ylabel("density")
            plt.legend()

            outpath = outdir / f"dist_buf{buf}_cache{cache}.png"
            plt.savefig(outpath, dpi=200, bbox_inches="tight")
            plt.close()

            print(f"[+] Wrote {outpath}")


def plot_means(summary, outdir):
    for cache in sorted(summary["cache"].unique()):
        subset = summary[summary["cache"] == cache]

        plt.figure()

        for impl in sorted(subset["impl"].unique()):
            s = subset[subset["impl"] == impl]
            plt.plot(s["buf"], s["mean"], marker="o", label=impl)

        plt.title(f"Mean AES timing by buffer size: cache={cache}")
        plt.xlabel("buffer size")
        plt.ylabel("mean ticks")
        plt.xscale("log", base=2)
        plt.legend()

        outpath = outdir / f"mean_cache{cache}.png"
        plt.savefig(outpath, dpi=200, bbox_inches="tight")
        plt.close()

        print(f"[+] Wrote {outpath}")


def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = LOG_ROOT / timestamp
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Output directory: {outdir}")

    run_benchmarks(outdir)

    df = load_logs(outdir)
    summary = summarize(df, outdir)

    plot_distributions(df, outdir)
    plot_means(summary, outdir)

    print("\n[+] Done")


if __name__ == "__main__":
    main()
