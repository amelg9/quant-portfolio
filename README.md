# Quant Portfolio — Finance, Data and Cloud

## Objective

This portfolio presents a set of quantitative finance projects designed to demonstrate three key abilities:

1. Financial data manipulation (tickers, prices, volatility, correlations)
2. Implementation of classical quantitative methods (backtesting, portfolio optimization, option pricing, risk modeling)
3. Industrialization of solutions (data pipelines, cloud architecture, CI/CD, APIs, dashboards)


## Portfolio Structure

Each project is an independent repository focusing on a specific skill area within quantitative finance.

| # | Project | Main Topic | 
|:-:|:--------|:------------|
| 1 | [quant-data-architecture](https://github.com/amelg9/quant-portfolio/tree/portfolio/data-architecture) | Data and Infrastructure | 
| 2 | [quant-analysis](https://github.com/amelg9/quant-portfolio/tree/portfolio/quantitative-anaysis) | Introductory NASDAQ Quant Analysis | 
| 3 | [quant-backtesting](https://github.com/<username>/quant-backtesting) | Strategy and Performance (not available on github yet) | 
| 4 | [quant-portfolio-optimization](https://github.com/<username>/quant-portfolio-optimization) | Portfolio Optimization (not available on github yet) |
| 5 | [quant-risk-modelling](https://github.com/<username>/quant-risk-modelling) | Volatility and Risk (not started) | 
| 6 | [quant-ml-finance (optional)](https://github.com/<username>/quant-ml-finance) | Machine Learning (not started) |

## Project Overview

### 1. Financial Data Pipeline (Done)

Goal: Build a cloud-based infrastructure to collect and store market data : NASDAQ, NYSE and NYSE American (previously AMEX)
Technologies: Python, Pub/Sub, BigQuery, Cloud Run, VM Instances. 
Includes scripts, an automated pipeline, and dashboard integration.  


### 2. Backtesting and Simple Strategies (Current Work)
Goal: Develop a lightweight backtesting framework and test several classical strategies:  
- Momentum (Moving Average Crossover)  
- Mean Reversion (Bollinger Bands)  
- Portfolio Rebalancing (60/40 Equity/Bond)  
Includes benchmark comparison with Buy & Hold.  

### 3. Portfolio Optimization (Current Work)
Goal: Implement and visualize the efficient frontier for a multi-asset portfolio.  
Constraints: weight limits, no short-selling, limited leverage  
Extensions: shrinkage covariance, Black-Litterman, risk-parity  
Visualization in 2D/3D.  

### 4. Volatility and Risk Modelling (not started)
Goal: Model and quantify portfolio risk using time-series techniques.  
Includes GARCH, EGARCH, Heston simulations, comparison of realized vs implied volatility, and Monte Carlo estimation of Value-at-Risk.  

### 5. Machine Learning for Finance (not started)
Goal: Explore ML methods for predicting returns or volatility.  
Models: LSTM, Random Forest  
Methodology: time-based train/test split, overfitting analysis, and model limitations.  

## Technical Organization

Each project follows a consistent structure:

project-name/
├── README.md
├── notebooks/
├── src/
├── tests/
├── requirements.txt
├── .gitignore
└── LICENSE


## Portfolio Presentation

This main repository serves as an index for all projects, with:
- An overview of the portfolio
- Visual slides and architecture diagrams
- References to each project repository

Example structure:
quant-portfolio/
├── README.md
├── projects/
│ ├── data-pipeline.md
│ ├── backtesting.md
│ ├── portfolio-optimization.md
│ └── risk-modelling.md
└── slides/
└── quant_portfolio_presentation.pdf


## Global Tech Stack

- Python (Pandas, NumPy, Scikit-learn, Statsmodels, Plotly)
- Google Cloud Platform (Pub/Sub, BigQuery, Cloud Run, Scheduler, VM Instances, Vertex AI)
- Docker, GitHub Actions (CI/CD)
- Jupyter, Streamlit, Looker Studio
- Quantitative Finance: Markowitz, GARCH, VaR, Machine Learning for time-series


## License

This portfolio is released under the MIT License.  
All notebooks and scripts are open-source for educational and demonstration purposes.
