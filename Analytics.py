"""
Delivery Service Analytics
Combines normalized Strava activity data with Uber earnings data.
All distances in miles, all times in minutes.
"""

import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt
import matplotlib.dates  as mdates
import re
import warnings
warnings.filterwarnings("ignore")

# ── 1. LOAD RAW DATA ─────────────────────────────────────────────────────────

strava_raw = pd.read_csv("Strava.csv")
uber_raw   = pd.read_csv("uber_earnings_bike.csv")

print(f"Strava raw:  {strava_raw.shape[0]} rides,   {strava_raw.shape[1]} columns")
print(f"Uber raw:    {uber_raw.shape[0]} orders,  {uber_raw.shape[1]} columns")


# ── 2. NORMALIZE STRAVA ───────────────────────────────────────────────────────

STRAVA_KEEP = [
    "name", "start_date_local", "distance", "moving_time",
    "elapsed_time", "total_elevation_gain", "average_speed",
    "max_speed", "kilojoules", "start_latlng", "end_latlng",
    "type", "sport_type"
]

strava = strava_raw[STRAVA_KEEP].copy()

# Parse datetime and extract date
strava["datetime"]     = pd.to_datetime(strava["start_date_local"])
strava["date"]         = strava["datetime"].dt.date
strava["hour"]         = strava["datetime"].dt.hour

# Convert units: meters → miles, seconds → minutes, m/s → mph
strava["distance_mi"]   = (strava["distance"]     / 1609.34).round(2)
strava["moving_min"]    = (strava["moving_time"]  / 60).round(1)
strava["elapsed_min"]   = (strava["elapsed_time"] / 60).round(1)
strava["avg_speed_mph"] = (strava["average_speed"] * 2.23694).round(2)
strava["max_speed_mph"] = (strava["max_speed"]     * 2.23694).round(2)

# Service ride flag
strava["is_service"] = strava["name"].str.contains(
    r"[Ss]ervice|Service run|Night service|Morning Service", regex=True
)

# Drop raw unit columns now that converted versions exist
strava.drop(columns=["distance", "moving_time", "elapsed_time",
                      "average_speed", "max_speed", "start_date_local"], inplace=True)

print("\n── Normalized Strava ──")
print(strava[["name","date","distance_mi","moving_min","avg_speed_mph",
              "kilojoules","is_service"]].to_string(index=False))


# ── 3. NORMALIZE UBER ─────────────────────────────────────────────────────────

uber = uber_raw.copy()

# Parse date: "Fri, May 22" → 2026-05-22
uber["date"] = pd.to_datetime(
    uber["date"].str.replace(r'^[A-Za-z]+,\s*', '', regex=True) + " 2026",
    format="%b %d %Y"
).dt.date

# Normalize time string — handle missing space before AM/PM ("9:01PM" → "9:01 PM")
uber["time_clean"] = uber["time"].str.replace(r'([APap][Mm])', r' \1', regex=True).str.strip()
uber["datetime"]   = pd.to_datetime(
    uber["date"].astype(str) + " " + uber["time_clean"],
    format="%Y-%m-%d %I:%M %p", errors="coerce"
)
uber["hour"] = uber["datetime"].dt.hour

# Normalize tip: blank → 0.0, "processing" → 0.0 (excluded — not yet settled)
uber["tip_usd"] = pd.to_numeric(
    uber["tip_usd"].replace("processing", np.nan), errors="coerce"
).fillna(0.0)

# Parse delivery_time string → decimal minutes ("34 min 34 sec" → 34.57)
def parse_delivery_time(s):
    if pd.isna(s):
        return np.nan
    m   = re.search(r'(\d+)\s*min', str(s))
    sec = re.search(r'(\d+)\s*sec', str(s))
    mins = int(m.group(1))   if m   else 0
    secs = int(sec.group(1)) if sec else 0
    return round(mins + secs / 60, 2)

uber["delivery_min"] = uber["delivery_time"].apply(parse_delivery_time)

# Parse distance string → float miles ("2.67 mi" → 2.67)
uber["distance_mi"] = uber["distance"].str.extract(r'([\d.]+)').astype(float)

# Derived metrics
uber["total_pay"]    = uber["earnings_usd"] + uber["tip_usd"]
uber["pay_per_mile"] = (uber["total_pay"] / uber["distance_mi"]).round(2)
uber["pay_per_min"]  = (uber["total_pay"] / uber["delivery_min"]).round(2)

# Drop original string columns now that parsed versions exist
uber.drop(columns=["time", "time_clean", "delivery_time", "distance"], inplace=True)

print("\n── Normalized Uber (first 8 rows) ──")
print(uber[["date","hour","vendor","earnings_usd","tip_usd","total_pay",
            "delivery_min","distance_mi","pay_per_mile"]].head(8).to_string(index=False))


# ── 4. DAILY SUMMARIES ────────────────────────────────────────────────────────

strava_daily = strava.groupby("date").agg(
    rides          = ("name",          "count"),
    total_dist_mi  = ("distance_mi",   "sum"),
    total_move_min = ("moving_min",    "sum"),
    total_kj       = ("kilojoules",    "sum"),
    avg_speed_mph  = ("avg_speed_mph", "mean"),
    service_rides  = ("is_service",    "sum"),
).round(2).reset_index()

uber_daily = uber.groupby("date").agg(
    orders          = ("earnings_usd",  "count"),
    gross_earnings  = ("earnings_usd",  "sum"),
    total_tips      = ("tip_usd",       "sum"),
    total_pay       = ("total_pay",     "sum"),
    total_del_dist  = ("distance_mi",   "sum"),
    avg_del_min     = ("delivery_min",  "mean"),
    avg_pay_per_mi  = ("pay_per_mile",  "mean"),
    avg_pay_per_min = ("pay_per_min",   "mean"),
).round(2).reset_index()

uber_daily["tip_rate_pct"] = (
    uber_daily["total_tips"] / uber_daily["gross_earnings"] * 100
).round(1)

print("\n── Daily Strava Summary ──")
print(strava_daily.to_string(index=False))

print("\n── Daily Uber Summary ──")
print(uber_daily.to_string(index=False))


# ── 5. JOIN ON DATE ───────────────────────────────────────────────────────────

combined = pd.merge(strava_daily, uber_daily, on="date", how="outer")
combined["date"] = pd.to_datetime(combined["date"])
combined.sort_values("date", inplace=True)
combined.reset_index(drop=True, inplace=True)

# Efficiency metrics — only valid on days where both datasets overlap
combined["earn_per_strava_mile"] = (
    combined["total_pay"] / combined["total_dist_mi"]
).round(2)

combined["earn_per_active_hour"] = (
    combined["total_pay"] / (combined["total_move_min"] / 60)
).round(2)

print("\n── Combined Daily View (overlap days) ──")
overlap = combined.dropna(subset=["total_pay", "total_dist_mi"])
print(overlap[["date","total_dist_mi","total_move_min","total_pay",
               "orders","earn_per_strava_mile","earn_per_active_hour"]].to_string(index=False))


# ── 6. EDA VISUALIZATIONS ─────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("Delivery Service Insights — EDA", fontsize=14, fontweight="bold")

# (a) Daily total pay over time
ax = axes[0, 0]
uber_plot = uber_daily.copy()
uber_plot["date"] = pd.to_datetime(uber_plot["date"])
ax.bar(uber_plot["date"], uber_plot["total_pay"], color="steelblue", width=0.6)
ax.set_title("Daily Total Pay (Uber)")
ax.set_ylabel("USD ($)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
ax.tick_params(axis="x", rotation=45)

# (b) Total pay per delivery distribution
ax = axes[0, 1]
ax.hist(uber["total_pay"], bins=15, color="seagreen", edgecolor="white")
ax.axvline(uber["total_pay"].mean(), color="red", linestyle="--",
           label=f"Mean ${uber['total_pay'].mean():.2f}")
ax.set_title("Total Pay Per Delivery")
ax.set_xlabel("USD ($)")
ax.set_ylabel("Count")
ax.legend()

# (c) Pay per mile distribution
ax = axes[0, 2]
valid_ppm = uber["pay_per_mile"].replace([np.inf, -np.inf], np.nan).dropna()
ax.hist(valid_ppm, bins=15, color="darkorange", edgecolor="white")
ax.axvline(valid_ppm.mean(), color="red", linestyle="--",
           label=f"Mean ${valid_ppm.mean():.2f}/mi")
ax.set_title("Pay Per Mile")
ax.set_xlabel("$/mile")
ax.set_ylabel("Count")
ax.legend()

# (d) Delivery time vs total pay
ax = axes[1, 0]
mask = uber["delivery_min"].notna()
ax.scatter(uber.loc[mask, "delivery_min"], uber.loc[mask, "total_pay"],
           alpha=0.6, color="purple", edgecolors="white", s=60)
m, b = np.polyfit(uber.loc[mask, "delivery_min"], uber.loc[mask, "total_pay"], 1)
x_line = np.linspace(uber["delivery_min"].min(), uber["delivery_min"].max(), 100)
ax.plot(x_line, m * x_line + b, "r--", alpha=0.8, label=f"Trend (slope={m:.2f})")
ax.set_title("Delivery Time vs Total Pay")
ax.set_xlabel("Delivery Time (min)")
ax.set_ylabel("Total Pay ($)")
ax.legend()

# (e) Delivery distance vs total pay
ax = axes[1, 1]
mask2 = uber["distance_mi"].notna()
ax.scatter(uber.loc[mask2, "distance_mi"], uber.loc[mask2, "total_pay"],
           alpha=0.6, color="teal", edgecolors="white", s=60)
m2, b2 = np.polyfit(uber.loc[mask2, "distance_mi"], uber.loc[mask2, "total_pay"], 1)
x_line2 = np.linspace(uber["distance_mi"].min(), uber["distance_mi"].max(), 100)
ax.plot(x_line2, m2 * x_line2 + b2, "r--", alpha=0.8, label=f"Trend (slope={m2:.2f})")
ax.set_title("Delivery Distance vs Total Pay")
ax.set_xlabel("Distance (miles)")
ax.set_ylabel("Total Pay ($)")
ax.legend()

# (f) Avg pay by hour of day
ax = axes[1, 2]
hourly = uber.groupby("hour")["total_pay"].mean()
ax.bar(hourly.index, hourly.values, color="coral", edgecolor="white")
ax.set_title("Avg Pay by Hour of Day")
ax.set_xlabel("Hour (24h)")
ax.set_ylabel("Avg Pay ($)")
ax.set_xticks(sorted(uber["hour"].dropna().unique().astype(int)))

plt.tight_layout()
plt.savefig("delivery_eda.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nPlot saved: delivery_eda.png")


# ── 7. KEY METRICS SUMMARY ────────────────────────────────────────────────────

print("\n" + "=" * 52)
print("KEY METRICS SUMMARY")
print("=" * 52)
print(f"  Total orders:              {len(uber)}")
print(f"  Total gross earnings:     ${uber['earnings_usd'].sum():.2f}")
print(f"  Total tips:               ${uber['tip_usd'].sum():.2f}")
print(f"  Total pay (incl. tips):   ${uber['total_pay'].sum():.2f}")
print(f"  Avg pay per order:        ${uber['total_pay'].mean():.2f}")
print(f"  Avg pay per mile:         ${valid_ppm.mean():.2f}")
print(f"  Avg delivery time:        {uber['delivery_min'].mean():.1f} min")
print(f"  Avg distance per order:   {uber['distance_mi'].mean():.2f} mi")
print(f"  Overall tip rate:         {uber['tip_usd'].sum()/uber['earnings_usd'].sum()*100:.1f}%")
print()
print(f"  Total Strava rides:       {len(strava)}")
print(f"  Total Strava distance:    {strava['distance_mi'].sum():.1f} mi")
print(f"  Total active time:        {strava['moving_min'].sum()/60:.1f} hrs")
print()
if len(overlap):
    print(f"  Overlap days (both):      {len(overlap)}")
    print(f"  Avg earn/Strava mile:     ${overlap['earn_per_strava_mile'].mean():.2f}")
    print(f"  Avg earn/active hour:     ${overlap['earn_per_active_hour'].mean():.2f}")
print("=" * 52)
