import os
import sqlite3
import time
import pandas as pd
from flask import Flask, render_template, send_from_directory, Response, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

DB_PATH = os.path.join(BASE_DIR, "db", "lab.db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")

REQUEST_COUNT = Counter(
    "web_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "web_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint"]
)


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    endpoint = request.endpoint or "unknown"
    duration = time.time() - request.start_time
    REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
    REQUEST_DURATION.labels(endpoint).observe(duration)
    return response


def read_text_file(path):
    if not os.path.exists(path):
        return "File not found."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_csv_preview(path, rows=10):
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    return df.head(rows).to_html(classes="table table-striped", index=False)


def read_db_preview():
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM unemployed LIMIT 10", conn)
        return df.to_html(classes="table table-striped", index=False)
    finally:
        conn.close()


@app.route("/")
def index():
    data_preview = read_db_preview()
    quality_report = read_text_file(os.path.join(REPORTS_DIR, "data_quality_report.md"))
    model_report = read_text_file(os.path.join(REPORTS_DIR, "model_report.md"))
    missing_preview = read_csv_preview(os.path.join(REPORTS_DIR, "missing_values.csv"))
    eda_preview = read_csv_preview(os.path.join(REPORTS_DIR, "eda_summary.csv"))
    corr_preview = read_csv_preview(os.path.join(REPORTS_DIR, "correlation.csv"))

    figures = []
    if os.path.exists(FIGURES_DIR):
        for name in os.listdir(FIGURES_DIR):
            if name.lower().endswith(".png"):
                figures.append(name)

    return render_template(
        "index.html",
        data_preview=data_preview,
        quality_report=quality_report,
        model_report=model_report,
        missing_preview=missing_preview,
        eda_preview=eda_preview,
        corr_preview=corr_preview,
        figures=figures,
    )


@app.route("/figures/<path:filename>")
def get_figure(filename):
    return send_from_directory(FIGURES_DIR, filename)


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)