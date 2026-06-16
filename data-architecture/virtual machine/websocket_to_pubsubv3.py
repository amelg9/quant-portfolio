import os
import json
import time
import logging
import threading
from typing import List
from google.cloud import bigquery, pubsub_v1
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from datetime import datetime
import pytz

POLYGON_API_KEY = "w3Ptqx9vtrlWWaCaKC9fu_l4mwQ7ULD6"
PROJECT_ID = "rugged-night-472112-i7"

TABLES = {
    "XNAS": {"dataset": "xnas_dataset", "table": "xnas_top150tickers_marketcap"},
    "XNYS": {"dataset": "xnys_dataset", "table": "xnys_top150tickers_marketcap"},
    "XASE": {"dataset": "xase_dataset", "table": "xase_top150tickers_marketcap"},
}

PUBSUB_TOPICS = {
    "XNAS": "xnas-websocket",
    "XNYS": "xnys-websocket",
    "XASE": "xase-websocket"
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

bq_client = bigquery.Client(project=PROJECT_ID)
pub_client = pubsub_v1.PublisherClient()


def market_is_open():
    ny_tz = pytz.timezone("America/New_York")
    now_ny = datetime.now(ny_tz)
    market_open = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    return now_ny.weekday() < 5 and market_open <= now_ny <= market_close


def get_tickers_from_bigquery(exchange: str):
    dataset = TABLES[exchange]["dataset"]
    table = TABLES[exchange]["table"]
    query = f"""
        SELECT DISTINCT ticker
        FROM `{PROJECT_ID}.{dataset}.{table}`
        WHERE ticker IS NOT NULL
    """
    df = bq_client.query(query).to_dataframe()
    tickers = set(df["ticker"].dropna().astype(str))
    logging.info(f"{exchange}: {len(tickers)} tickers fetched from {dataset}.{table}")
    return tickers


def init_pubsub_topic(exchange: str):
    topic_name = PUBSUB_TOPICS[exchange]
    return pub_client.topic_path(PROJECT_ID, topic_name)


def timestamp_to_iso(ts_ms):
    if ts_ms is None:
        return None
    return datetime.utcfromtimestamp(ts_ms / 1000).isoformat() + "Z"


def handle_msg(msgs: List[WebSocketMessage]):
    global all_tickers_by_exchange
    for m in msgs:
        try:
            symbol = getattr(m, "symbol", None)
            if not symbol:
                continue

            if not market_is_open():
                continue

            for exchange, tickers in all_tickers_by_exchange.items():
                if symbol in tickers:
                    topic_path = init_pubsub_topic(exchange)
                    payload = {
                        "exchange": exchange,
                        "symbol": symbol,
                        "event_type": getattr(m, "event_type", None),
                        "volume": getattr(m, "volume", None),
                        "accumulated_volume": getattr(m, "accumulated_volume", None),
                        "official_open_price": getattr(m, "official_open_price", None),
                        "vwap": getattr(m, "vwap", None),
                        "open": getattr(m, "open", None),
                        "close": getattr(m, "close", None),
                        "high": getattr(m, "high", None),
                        "low": getattr(m, "low", None),
                        "aggregate_vwap": getattr(m, "aggregate_vwap", None),
                        "average_size": getattr(m, "average_size", None),
                        "start_timestamp": timestamp_to_iso(getattr(m, "start_timestamp", None)),
                        "end_timestamp": timestamp_to_iso(getattr(m, "end_timestamp", None)),
                        "ingestion_time": datetime.utcnow().isoformat() + "Z",
                    }
                    data = json.dumps(payload).encode("utf-8")
                    future = pub_client.publish(topic_path, data=data)
                    try:
                        future.result(timeout=5)
                        logging.info(f"✅ Published: {symbol} → {exchange}")
                    except Exception as e:
                        logging.error(f"⚠️ Publish failed for {symbol}: {e}")
                    break
        except Exception as e:
            logging.error(f"Error in handle_msg: {e}")


def refresh_tickers_every(hours: float = 12):
    global all_tickers_by_exchange
    last_refresh = 0
    while True:
        now = time.time()
        if now - last_refresh > hours * 3600:
            logging.info("♻️ Refreshing tickers from BigQuery...")
            all_tickers_by_exchange = {ex: get_tickers_from_bigquery(ex) for ex in TABLES}
            last_refresh = now
        time.sleep(300)


def run_forever():
    while True:
        try:
            logging.info("🔌 Connecting to Polygon WebSocket...")
            client = WebSocketClient(
                api_key=POLYGON_API_KEY,
                feed=Feed.Delayed,
                market=Market.Stocks,
            )
            client.subscribe("AM.*")
            client.run(handle_msg)
        except Exception as e:
            logging.error(f"WebSocket error: {e}. Reconnecting in 10s...")
            pub_client.transport._publisher._batcher._stop_all()
            time.sleep(10)


if __name__ == "__main__":
    logging.info("🚀 Starting Polygon WebSocket → Pub/Sub service")
    all_tickers_by_exchange = {ex: get_tickers_from_bigquery(ex) for ex in TABLES}
    refresh_thread = threading.Thread(target=refresh_tickers_every, args=(12,), daemon=True)
    refresh_thread.start()
    run_forever()
