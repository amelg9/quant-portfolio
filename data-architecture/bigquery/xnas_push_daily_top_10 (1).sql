-- Example of scheduled query running on bigquery.
-- Purpose: extract the 10 largest daily stock price increases on XNAS, the same scheduled query exists for top 10 decreases
-- ... and for each exchange I work with.
-- Frequency: once per day (BigQuery scheduled query). 
-- Destination: xnas_dataset.xnas_daily_top_10.

WITH base AS (
  SELECT
    symbol,
    start_timestamp,
    DATETIME(start_timestamp, 'America/New_York') AS ny_dt,
    open,
    close
  FROM `project-id.xnas_dataset.xnas_live_data`
),

last_day AS (
  SELECT
    DATE(MAX(ny_dt)) AS day ####à modifier pour la date
  FROM base
),

day_data AS (
  SELECT b.*
  FROM base b
  JOIN last_day l
  ON DATE(b.ny_dt) = l.day
),

opening_prices AS (
  SELECT
    symbol,
    open AS open_price_day,
    ny_dt AS open_timestamp_ny
  FROM (
    SELECT
      symbol,
      open,
      ny_dt,
      ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY ny_dt ASC) AS rn
    FROM day_data
    WHERE (EXTRACT(HOUR FROM ny_dt) > 9)
       OR (EXTRACT(HOUR FROM ny_dt) = 9 AND EXTRACT(MINUTE FROM ny_dt) >= 30)
  )
  WHERE rn = 1
),

closing_prices AS (
  SELECT
    symbol,
    close AS close_price_day,
    ny_dt AS close_timestamp_ny
  FROM (
    SELECT
      symbol,
      close,
      ny_dt,
      ROW_NUMBER() OVER(PARTITION BY symbol ORDER BY ny_dt DESC) AS rn
    FROM day_data
    WHERE (EXTRACT(HOUR FROM ny_dt) < 16)
       OR (EXTRACT(HOUR FROM ny_dt) = 16 AND EXTRACT(MINUTE FROM ny_dt) <= 0)
  )
  WHERE rn = 1
),

daily_prices AS (
  SELECT
    o.symbol,
    (SELECT day FROM last_day) AS day,
    o.open_price_day,
    c.close_price_day,
    o.open_timestamp_ny,
    c.close_timestamp_ny
  FROM opening_prices o
  JOIN closing_prices c USING(symbol)
),

daily_variation AS (
  SELECT
    d.day,
    d.symbol,
    d.open_price_day,
    d.close_price_day,
    SAFE_DIVIDE(d.close_price_day - d.open_price_day, d.open_price_day) * 100 AS variation_pct,
    d.open_timestamp_ny,
    d.close_timestamp_ny,
    CASE
      WHEN MAX(EXTRACT(HOUR FROM ny_dt)) >= 16 THEN 'complete'
      WHEN MAX(EXTRACT(HOUR FROM ny_dt)) >= 9 THEN 'in_progress'
      ELSE 'before_open'
    END AS market_status
  FROM day_data
  JOIN daily_prices d USING(symbol)
  GROUP BY d.day, d.symbol, d.open_price_day, d.close_price_day, d.open_timestamp_ny, d.close_timestamp_ny
)

SELECT *
FROM daily_variation
QUALIFY ROW_NUMBER() OVER(PARTITION BY day ORDER BY variation_pct DESC) <= 10;


