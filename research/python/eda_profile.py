"""Reusable EDA profile for a prepared research CSV.

Example:
  python research/python/eda_profile.py data/processed/panel.csv --value value --group country
Outputs summary tables and diagnostic plots. ADF is only a univariate diagnostic;
select transformations and test specifications based on the data-generating process.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--value", default="value")
    parser.add_argument("--date", default="year")
    parser.add_argument("--group", default="countryiso3code")
    parser.add_argument("--out", type=Path, default=Path("artifacts/eda"))
    args = parser.parse_args()
    df = pd.read_csv(args.csv)
    args.out.mkdir(parents=True, exist_ok=True)

    df.describe(include="all").transpose().to_csv(args.out / "describe.csv")
    missing = df.isna().mean().sort_values(ascending=False).rename("missing_fraction")
    missing.to_csv(args.out / "missingness.csv")
    plt.figure(figsize=(10, 5))
    missing.head(40).sort_values().plot(kind="barh")
    plt.title("Missingness fraction by variable")
    plt.tight_layout()
    plt.savefig(args.out / "missingness.png", dpi=150)
    plt.close()

    numeric = df.select_dtypes(include="number")
    numeric.corr().to_csv(args.out / "correlation.csv")
    if len(numeric.columns) >= 2:
        corr = numeric.corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(corr, aspect="auto", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr.columns)), corr.columns, rotation=90)
        ax.set_yticks(range(len(corr.index)), corr.index)
        fig.colorbar(im, ax=ax, label="Pearson correlation")
        ax.set_title("Numeric-variable correlation")
        fig.tight_layout()
        fig.savefig(args.out / "correlation.png", dpi=150)
        plt.close(fig)

    if args.value in df.columns and args.date in df.columns:
        plot_df = df.copy()
        plot_df[args.value] = pd.to_numeric(plot_df[args.value], errors="coerce")
        plot_df[args.date] = pd.to_numeric(plot_df[args.date], errors="coerce")
        group_col = args.group if args.group in plot_df.columns else None
        selected = plot_df[group_col].dropna().astype(str).iloc[0] if group_col and plot_df[group_col].notna().any() else None
        if group_col and selected is not None:
            series_df = plot_df.loc[plot_df[group_col].astype(str) == selected]
        else:
            series_df = plot_df
        series_df = series_df.dropna(subset=[args.date, args.value]).sort_values(args.date)
        if len(series_df) >= 3:
            plt.figure(figsize=(10, 5))
            plt.plot(series_df[args.date], series_df[args.value])
            plt.title(f"{args.value} over time" + (f" — {selected}" if selected else ""))
            plt.xlabel(args.date)
            plt.ylabel(args.value)
            plt.tight_layout()
            plt.savefig(args.out / "series.png", dpi=150)
            plt.close()
            values = series_df[args.value].astype(float)
            tests = {}
            try:
                tests["adf_pvalue"] = float(adfuller(values, autolag="AIC")[1])
            except Exception as exc:
                tests["adf_error"] = str(exc)
            try:
                tests["kpss_pvalue"] = float(kpss(values, regression="c", nlags="auto")[1])
            except Exception as exc:
                tests["kpss_error"] = str(exc)
            pd.Series(tests, name="result").to_csv(args.out / "unit_root_tests.csv")
    print(f"EDA artifacts written to {args.out.resolve()}")


if __name__ == "__main__":
    main()
