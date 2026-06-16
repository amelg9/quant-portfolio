"""
Code of a Cloud run function that fetches the top 150 stocks by market capitalization from the New York Stock Exchange (XNYS)
using the Polygon.io API, then publishes the results to a dedicated Google Cloud Pub/Sub topic.

Part of a daily Cloud Run workflow, with similar scripts for NASDAQ (XNAS) and NYSE AMERICAN (XASE).
Executions are offset to prevent API token overlap, see README in current folder for more information.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from polygon import RESTClient
from requests.exceptions import RequestException
from tqdm import tqdm
from google.cloud import pubsub_v1

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')



POLYGON_API_KEY = os.environ.get("api_key")
OUTPUT_DIR = "./"
TOP_N = 150
EXCHANGES = ["XNYS"]  # XNAS, XNYS, XASE
MAX_TICKERS = 6000     
MAX_WORKERS = 5       
SLEEP_BETWEEN_BATCHES = 0.2

GCP_PROJECT = "x"
PUBSUB_TOPIC = "xnys-top150-tickers-marketcap"  

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def safe_extract_market_cap(details):
    try:
        if isinstance(details, dict):
            res = details.get("results", details)
        else:
            res = getattr(details, "results", None) or details

        if isinstance(res, dict):
            mcap = res.get("market_cap") or res.get("marketCap")
            if mcap is None:
                mcap = details.get("market_cap") if isinstance(details, dict) else None
            return int(mcap) if mcap else 0

        if hasattr(res, "market_cap"):
            return int(getattr(res, "market_cap") or 0)
        if hasattr(res, "marketCap"):
            return int(getattr(res, "marketCap") or 0)
        return 0
    except Exception:
        return 0


def get_tickers_for_exchange(client, exchange, max_tickers=MAX_TICKERS):
    tickers = []
    for t in client.list_tickers(type="CS", market="stocks", exchange=exchange, active=True, limit=100, sort="ticker"):
        try:
            ticker_str = t.ticker if hasattr(t, "ticker") else (t.get("ticker") if isinstance(t, dict) else None)
        except Exception:
            ticker_str = None
        if not ticker_str:
            continue
        tickers.append(ticker_str)
        if len(tickers) >= max_tickers:
            break
    logging.info(f"{exchange}: {len(tickers)} tickers chargés depuis Polygon (max {max_tickers})")
    return tickers


def fetch_market_cap_worker(client, ticker, sleep_between=0.0):
    try:
        details = client.get_ticker_details(ticker)
        mcap = safe_extract_market_cap(details)
    except RequestException:
        time.sleep(0.5)
        try:
            details = client.get_ticker_details(ticker)
            mcap = safe_extract_market_cap(details)
        except Exception:
            mcap = 0
    except Exception:
        mcap = 0

    if sleep_between:
        time.sleep(sleep_between)
    return ticker, mcap


def get_market_caps_parallel(client, tickers, max_workers=MAX_WORKERS, sleep_between=SLEEP_BETWEEN_BATCHES):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_market_cap_worker, client, t, sleep_between): t for t in tickers}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Fetching market caps"):
            try:
                ticker, mcap = fut.result()
                results.append({"ticker": ticker, "market_cap": mcap})
            except Exception:
                ticker = futures[fut]
                results.append({"ticker": ticker, "market_cap": 0})
    return results


def init_publisher():
    if not GCP_PROJECT or not PUBSUB_TOPIC:
        raise ValueError("GCP_PROJECT et PUBSUB_TOPIC doivent être définis (env vars ou dans le script).")
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCP_PROJECT, PUBSUB_TOPIC)
    return publisher, topic_path


def publish_top_rows(publisher, topic_path, df):
    publish_futures = []

    for _, row in df.iterrows():
        payload = {
            "ticker": str(row["ticker"]),
            "market_cap": int(row["market_cap"]),
            "exchange": row.get("exchange", ""),
            "timestamp": row.get("timestamp", datetime.now(timezone.utc).isoformat())
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        future = publisher.publish(topic_path, data=data_bytes, origin="polygon-script")
        publish_futures.append(future)

    summary_payload = {
        "exchange": df["exchange"].iloc[0] if not df.empty else "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "top_list": df[["ticker", "market_cap"]].to_dict(orient="records")
    }
    summary_bytes = json.dumps(summary_payload).encode("utf-8")
    future_summary = publisher.publish(topic_path, data=summary_bytes, origin="polygon-script", type="summary")
    publish_futures.append(future_summary)

    results = []
    for f in publish_futures:
        try:
            msg_id = f.result(timeout=30)  # attente jusqu'à 30s par publish
            results.append(msg_id)
        except Exception as e:
            logging.error(f"Erreur lors de la publication Pub/Sub: {e}")
            results.append(None)
    logging.info(f"Pub/Sub: {len(results)} messages publiés (IDs partiels/None si erreur).")
    return results


def process_exchange(client, publisher, topic_path, exchange):
    tickers = get_tickers_for_exchange(client, exchange, MAX_TICKERS)
    logging.info(f"📊 {exchange}: récupération des market caps pour {len(tickers)} tickers (parallèle)...")

    data = get_market_caps_parallel(client, tickers, max_workers=MAX_WORKERS, sleep_between=SLEEP_BETWEEN_BATCHES)

    df = pd.DataFrame(data)
    df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce").fillna(0).astype("int64")
    df = df.sort_values(by="market_cap", ascending=False).head(TOP_N)
    df["exchange"] = exchange
    df["timestamp"] = datetime.now(timezone.utc).isoformat()

    try:
        publish_top_rows(publisher, topic_path, df)
    except Exception as e:
        logging.error(f"Erreur lors de la publication Pub/Sub pour {exchange}: {e}")

    return df


def main(request):
    logging.info("Lancement du filtrage top tickers Polygon + publication Pub/Sub")
    client = RESTClient(POLYGON_API_KEY)
    try:
        publisher, topic_path = init_publisher()
    except Exception as e:
        logging.error(f"Impossible d'initialiser Pub/Sub publisher: {e}")
        return

    for exchange in EXCHANGES:
        df = process_exchange(client, publisher, topic_path, exchange)
        logging.info(f"{exchange}: top 5 ->\n{df.head(5).to_string(index=False)}")

    logging.info("Traitement terminé.")
    return "Traitement terminé", 200


#if __name__ == "__main__":
#    main()
