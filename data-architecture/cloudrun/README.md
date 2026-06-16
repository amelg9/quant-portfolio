
# CLOUD RUN DEPLOYMENT

This project runs three independent Cloud Run services, each dedicated to a U.S. stock exchange:

- **XNYS** – New York Stock Exchange  
- **XNAS** – NASDAQ  
- **XASE** – NYSE American  

Each service executes a Python script that fetches the top 150 stocks by market capitalization from the Polygon.io API and publishes the results to a dedicated Google Cloud Pub/Sub topic.  
A downstream Pub/Sub subscription automatically writes messages to BigQuery, storing the data in a partitioned table for analysis and backtesting.

---

## ARCHITECTURE OVERVIEW

Cloud Scheduler triggers the services sequentially between 23:00 and 23:30 (UTC+2), with 10-minute intervals to avoid API rate limits:

23:00 → Cloud Run: xnys-get-top150tickers
23:10 → Cloud Run: xnas-get-top150tickers
23:20 → Cloud Run: xase-get-top150tickers

yaml
Copier le code

Each service fetches tickers, retrieves market caps in parallel, sorts by market cap, and publishes the top 150 to Pub/Sub.

---

## DEPLOYMENT

Each Cloud Run service is deployed as a standalone container image.  
The services are triggered nightly by Cloud Scheduler, ensuring a sequential workflow without overlap.

---

## DATA FLOW

1. Cloud Scheduler triggers Cloud Run jobs nightly.  
2. Cloud Run fetches ticker data from Polygon.io.  
3. Top 150 tickers with market caps are published to Pub/Sub.  
4. Pub/Sub subscription writes messages into BigQuery, partitioned by ingestion date.  

This setup provides a reliable, daily snapshot of major U.S. equity markets, ready for analytics, dashboards, or backtesting.
