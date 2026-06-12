# Introductory Quantitative Analysis Notebook

This notebook provides a **basic introduction to quantitative analysis** using minute-level NASDAQ data. It is designed as a first step for exploring market data, computing indicators, testing simple strategies, and performing portfolio simulations. The goal is to offer a hands-on experience before building a more structured and fully-featured GitHub repository with separate modules and scripts.

**Note**: This notebook aims to **demonstrate basic tools and workflows** for data analysis and quantitative finance, rather than to produce exploitable or production-level insights. Calculations are performed on a **limited dataset**, as the cloud data ingestion architecture has only been operational since mid-October 2025.


## Overview

The notebook is organized into several blocks:

1. **Imports & Setup**  
   Load Python libraries (Pandas, NumPy, Matplotlib, Backtrader), configure display options, and initialize the BigQuery client.

2. **Load Data**  
   Load the last two weeks of minute-level NASDAQ data from BigQuery, filter for top tickers or a sample set for faster execution, clean the data (drop NaNs, remove duplicates, convert timestamps to UTC).

3. **Basic Stats & Exploratory Data Analysis (EDA)**  
   Count data points per ticker, compute basic statistics (mean, min, max, volatility), plot histograms of returns, and visualize sample ticker price evolution.

4. **Returns & Indicators**  
   Compute log returns, rolling statistics (15-minute and 1-hour moving averages), rolling volatility, and Bollinger Bands for a mean-reversion demonstration. Visualize indicators for a sample ticker.

5. **Simple Strategy #1 — Moving Average Crossover**  
   Implement a basic trading strategy: buy when the short-term MA crosses above the long-term MA, sell otherwise. Run a backtest on a few tickers and compute cumulative returns, Sharpe ratio, and max drawdown.

6. **Simple Strategy #2 — Mean Reversion via Bollinger Bands**  
   Buy when the price falls below the lower Bollinger Band and sell when it rises above the upper band. Run a backtest and compare to a benchmark.

7. **Market Portfolio Simulation (Simulated NASDAQ Index)**  
   Construct a portfolio of the most traded tickers to simulate a **market index**. Compute cumulative returns, Sharpe ratio, and max drawdown to evaluate the simulated index performance.

8. **Monte Carlo Basic Simulation & Backtest**  
   Generate multiple random portfolios to explore different compositions, backtest them, and identify top-performing portfolios. Visualize portfolio performance and cumulative returns.

## Technical Setup

- The notebook runs on a **Vertex AI Notebook instance**.  
- Data is retrieved from **BigQuery** for fast access to high-frequency trading data.  
- Plots are generated with **Matplotlib** and styled for clarity.  
- The notebook focuses on **introductory-level quantitative analysis** and can be extended for more advanced strategies and metrics.

## Usage

1. Launch the notebook on Vertex AI.  
2. Make sure the BigQuery client is authenticated and has access to your dataset.  
3. Run the cells sequentially to explore data, compute indicators, backtest strategies, and analyze portfolio simulations.

---

This notebook is intended as a **learning tool** and a foundation for building a more structured and modular quantitative analysis repository.
