Virtual Machine: Polygon WebSocket → Pub/Sub Service
Overview
This directory contains the Python service deployed on a Google Compute Engine (GCE) virtual machine.
Its purpose is to maintain a continuous data pipeline between the Polygon.io WebSocket API and Google Pub/Sub, ensuring real-time (or delayed) stock market data is streamed and made available for downstream analytics in BigQuery and Looker.

The service is designed to run without interuption on a lightweight Debian VM, using systemd for automatic startup and recovery. A scheduled cloud run function has been added to shutdown the VM during the weekend, when markets are closed.

VM Configuration
Setting	Value
Instance name	finance2
Region / Zone	europe-west9-b
Machine type	e2-small (2 vCPUs, 2 GB memory)
OS image	Debian 12 (Bookworm)
Architecture	x86_64
Python version	3.13
Status	Running during open market days via systemd and shut down during weekends
The VM runs a single service responsible for ingesting and publishing market data.

Service Description
File: websocket_to_pubsub.py
Language: Python 3.13
Dependencies:

google-cloud-bigquery
google-cloud-pubsub
polygon
pandas (for temporary DataFrame operations)
Main Features
Connects to the Polygon.io WebSocket API (Feed.Delayed, Market.Stocks)
Fetches ticker lists from BigQuery for NASDAQ, NYSE, and AMEX
Publishes live price and volume data to Google Pub/Sub topics:
xnas-websocket
xnys-websocket
xase-websocket
Automatically refreshes ticker lists every 12 hours
Handles reconnections and message buffering gracefully
Designed as a lightweight data ingestion layer for the analytics pipeline
Systemd Service
The Python process is managed by systemd to ensure reliability and automatic restart on failure.

Service Unit Example
[Unit]
Description=Polygon WebSocket to Pub/Sub
After=network.target

[Service]
Type=simple
User=<username>
WorkingDirectory=/home/<username>/polygon
ExecStart=/home/<username>/polygon/venv/bin/python /home/<username>/polygon/websocket_to_pubsub.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
Automation and Scheduling
The VM does not run continuously to reduce costs. Its lifecycle is managed using Cloud Run and Cloud Scheduler.

Cloud Scheduler triggers a Cloud Run job before U.S. market hours
The job starts the VM automatically
After market close or during weekends, the job stops the VM
Ensures the service runs only when data ingestion is required, optimizing cloud costs
Monitoring and Logging
All output from the Python service is captured in the systemd journal.

Real-time logs can be viewed with: journalctl -u polygon.service -f
The service handles reconnections and flushes pending messages on WebSocket errors
Each published message includes an ingestion timestamp, ensuring traceability in BigQuery
Data Flow
The VM acts as the first step in the financial data pipeline:

Polygon WebSocket → VM (Python ingestion service) → Pub/Sub → BigQuery → Looker

Polygon WebSocket: Provides real-time/delayed stock market events
VM Service (Python): Ingests messages, enriches them, publishes to Pub/Sub
Pub/Sub: Distributes messages to downstream consumers
BigQuery: Stores and organizes structured stock market data
Looker: Visualizes data for analytics and dashboards
This design balances reliability, cost efficiency, and low-latency ingestion.
