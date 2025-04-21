
# The Day the Water Stopped: What I Learned During a Seven-Month Drought

This repository contains the data, code, and visualizations for the article:
["The Day the Water Stopped"](https://timgraettinger.com/articles/the-day-the-water-stopped/)  
published on April 21, 2025.

## 🌱 Project Summary

When our home’s water supply stopped during a drought, 
I began collecting data from our holding tank 
and learning about local drought conditions. 
This project brings that story to life 
through visualizations and analysis.

## 📁 Contents

- `data/` — Source datasets (holding tank levels, county-level drought info)
- `docs/` — The PDF version of the article
- `figs/` — Final visualizations
- `src/`  — Code used to generate the chart
- `README.md` — This file
- `LICENSE` — License info

## 📊 Running the Code

To regenerate the drought vs. water-level plot:

```bash
python src/plot-holding-tank-water-level-and-drought-monitor.py
