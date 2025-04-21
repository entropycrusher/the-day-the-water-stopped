# -*- coding: utf-8 -*-
"""
Created on Fri Apr 11 09:07:02 2025

@author: Tim with Janet
"""

import matplotlib.pyplot as plt
import os
import pandas            as pd

# Constants and parameters
WATER_LEVEL_CSV = r"D:/vip/data/holding-tank-water-level.csv"
DROUGHT_CSV     = r"D:/vip/data/usdm-washington-county-pa-2000-to-present.csv"
PLOT_FOLDER     = r"D:/vip/figs/"

START_DATE      = pd.Timestamp("2024-05-01")
END_DATE        = pd.Timestamp("2025-04-09")

FIGURE_SIZE     = (11, 8.5)
DROUGHT_COLORS  = ["maroon", "red", "orange", "navajowhite", "yellow"]
DROUGHT_LABELS  = ["D4",     "D3",  "D2",     "D1",          "D0"]

TANK_TOP    = 27.5   # in inches
TANK_BOTTOM = 88



# Load and clean the water level data
df_water = pd.read_csv(WATER_LEVEL_CSV, parse_dates=[['Date', 'TimeOfDay']])
df_water['Date_TimeOfDay'] = pd.to_datetime(df_water['Date_TimeOfDay'], errors='coerce')
df_water = df_water.dropna(subset=['Date_TimeOfDay'])
df_water.set_index('Date_TimeOfDay', inplace=True)

# Get max depth per day for those days with multiple values
df_daily_water = df_water['WaterLevel_inches'].resample('D').max()


# Load and prep the drought data
df_drought = pd.read_csv(DROUGHT_CSV, parse_dates=['ValidStart'])
df_drought.set_index('ValidStart', inplace=True)

# Filter by date range
df_drought = df_drought.sort_index()
df_drought = df_drought.loc[START_DATE:END_DATE]
df_daily_water = df_daily_water.loc[START_DATE:END_DATE]

# Compute stacked values
drought_levels = ['D0', 'D1', 'D2', 'D3', 'D4']
df_stack = df_drought[drought_levels].fillna(0)
df_stack = df_stack.clip(lower=0, upper=100)  # Safety check

# Build the 'diff' values to remove overlaps from cumulative columns
df_stack["D0_only"] = df_stack["D0"] - df_stack["D1"]
df_stack["D1_only"] = df_stack["D1"] - df_stack["D2"]
df_stack["D2_only"] = df_stack["D2"] - df_stack["D3"]
df_stack["D3_only"] = df_stack["D3"] - df_stack["D4"]
df_stack["D4_only"] = df_stack["D4"]

# Reorder the dataframe to match plotting order (D4 on top)
df_stackplot = df_stack[["D4_only", "D3_only", "D2_only", "D1_only", "D0_only"]]


########## Build the plot ##########
fig, ax1 = plt.subplots(figsize=FIGURE_SIZE)

# Plot the clean stack with reordered levels
colors = DROUGHT_COLORS
labels = DROUGHT_LABELS
stack_handles = ax1.stackplot(df_stackplot.index, df_stackplot.T, labels=labels, colors=colors)
ax1.set_ylabel("Percent of County Area")
ax1.set_ylim(0, 100)

# Reference lines for year change
years = pd.date_range(start=START_DATE, end=END_DATE, freq='YS')
for y in years:
    ax1.axvline(x=y, color='gray', linestyle='--', alpha=0.3)

# Format x-axis with stacked Month + Year
month_locs = pd.date_range(start=START_DATE, end=END_DATE, freq='MS')
month_labels = [dt.strftime('%b\n%Y') for dt in month_locs]
ax1.set_xticks(month_locs)
ax1.set_xticklabels(month_labels, ha='center')

# Water level overlay (interpolated)
ax2 = ax1.twinx()
df_daily_water_interp = df_daily_water.interpolate(method='time')
ax2.plot(df_daily_water_interp.index, df_daily_water_interp.values,
         color='steelblue', linewidth=2, label='Tank Water Level')

# Add horizontal reference lines for tank top and bottom
ax2.axhline(TANK_TOP, color='gray', linestyle=':', linewidth=1)
ax2.text(
    df_daily_water.index.max() - pd.Timedelta(days=7),
    TANK_TOP - 1.5, "Top of Tank",
    color='gray', fontsize=9, va='top', ha='right'
)

ax2.axhline(TANK_BOTTOM, color='gray', linestyle=':', linewidth=1)
ax2.text(
    df_daily_water.index.max() - pd.Timedelta(days=7), 
    TANK_BOTTOM - 0.5, "Bottom of Tank",
    color='gray', fontsize=9, va='bottom', ha='right'
)

ax2.set_ylabel("Tank Depth (inches)", color='steelblue')
ax2.tick_params(axis='y', labelcolor='steelblue')
ax2.invert_yaxis()  # More water = higher line

# Triangle marker and text for fill events
fill_events = [
    ("2024-09-05", "Fill 1"),
    ("2024-11-12", "Fill 2")
]

for date_str, label in fill_events:
    event_date = pd.to_datetime(date_str)

    # Vertical line
    #ax2.axvline(event_date, color='darkblue', linestyle='--', linewidth=1)

    # Triangle marker
    ax2.plot(event_date, 27, marker='v', color='steelblue', markersize=8)

    # Label next to triangle
    ax2.text(
        event_date, 25, label, color='steelblue',
        fontsize=9, ha='center', va='top', fontweight='bold'
    )


# Title
ax1.set_title(f"Drought Conditions overlaid with Water Tank Level\n{START_DATE.date()} thru {END_DATE.date()}")

# Legend (bottom, outside plot)
handles = stack_handles + [ax2.lines[0]]
labels += ["Tank Water Level"]
fig.legend(handles, labels, loc='lower center', ncol=6, frameon=False, bbox_to_anchor=(0.5, -0.05))

# Layout
ax1.set_xlim(START_DATE, END_DATE)
fig.tight_layout(rect=[0, 0.03, 1, 1])  # Leave room for legend

# Save the plot to a file
FILENAME = f"drought-vs-waterlevel_{START_DATE.date()}_to_{END_DATE.date()}.png"
FILEPATH = os.path.join(PLOT_FOLDER, FILENAME)

fig.savefig(FILEPATH, dpi=300, bbox_inches='tight')
print(f"Saved plot to {FILEPATH}")
plt.show()
