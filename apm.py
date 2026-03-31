"""
APM instrumentation for Flask microservices.
Drop this file into any service and call setup_metrics(app).

Exposes:
  - HTTP request count, latency, errors (per route / method / status)
  - Process memory & CPU
  - Custom business metrics (LLM latency, cache hits, active sessions)

Endpoint: GET /metrics  (scraped by Prometheus)
"""
import time
import os
import logging

from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry,
    multiprocess, REGISTRY,
)
from flask import request, g

logger = logging.getLogger(__name__)

# ── Shared metric definitions (created once, referenced everywhere) ───────────

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['service', 'method', 'endpoint', 'status'],
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['service', 'method', 'endpoint'],
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10, 30, 60],
)

REQUEST_ERRORS = Counter(
    'http_request_errors_total',
    'Total HTTP 5xx errors',
    ['service', 'endpoint'],
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Currently in-flight HTTP requests',
    ['service'],
)

SERVICE_INFO = Info('service_info', 'Service metadata')

# ── Custom business metrics (used by individual services) ─────────────────────

LLM_REQUEST_COUNT = Counter(
    'llm_requests_total',
    'Total LLM calls made',
    ['service', 'model', 'status'],
)

LLM_LATENCY = Histogram(
    'llm_request_duration_seconds',
    'LLM response latency',
    ['service', 'model'],
    buckets=[1, 2, 5, 10, 20, 30, 60, 90, 120],
)

LLM_TOKEN_COUNT = Counter(
    'llm_tokens_total',
    'Estimated tokens processed',
    ['service', 'role'],
)

CACHE_OPS = Counter(
    'cache_operations_total',
    'Redis cache operations',
    ['service', 'operation', 'result'],   # result: hit | miss | error
)

DB_QUERY_LATENCY = Histogram(
    'db_query_duration_seconds',
    'Database query latency',
    ['service', 'operation'],
    buckets=[.001, .005, .01, .025, .05, .1, .25, .5, 1, 2],
)

CHAT_SESSIONS_ACTIVE = Gauge(
    'chat_sessions_active_total',
    'Total chat sessions in the database',
)

CHAT_MESSAGES_TOTAL = Counter(
    'chat_messages_total',
    'Total chat messages processed',
    ['role'],
)

MEMORY_FACTS_TOTAL = Gauge(
    'user_memory_facts_total',
    'Total user memory facts stored',
)

AUTH_ATTEMPTS = Counter(
    'auth_attempts_total',
    'Authentication attempts',
    ['service', 'result'],   # result: success | failure
)

API_KEY_USAGE = Counter(
    'api_key_usage_total',
    'API key usage',
    ['status'],              # status: valid | invalid | rate_limited
)


# ── Flask integration ──────────────────────────────────────────────────────────

def setup_metrics(app, service_name: str):
    """
    Attach Prometheus instrumentation to a Flask app.
    Call this in create_app() after the app is configured.
    """
    SERVICE_INFO.info({
        'name':    service_name,
        'version': '1.0.0',
        'env':     os.getenv('FLASK_ENV', 'production'),
    })

    # ── Expose /metrics endpoint ──────────────────────────────────────────────
    @app.route('/metrics')
    def metrics_endpoint():
        from flask import Response
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    # ── Before-request: start timer ───────────────────────────────────────────
    @app.before_request
    def before_request():
        g._start_time = time.time()
        ACTIVE_REQUESTS.labels(service=service_name).inc()

    # ── After-request: record metrics ─────────────────────────────────────────
    @app.after_request
    def after_request(response):
        latency  = time.time() - getattr(g, '_start_time', time.time())
        endpoint = _clean_endpoint(request.path)
        method   = request.method
        status   = str(response.status_code)

        REQUEST_COUNT.labels(
            service=service_name, method=method,
            endpoint=endpoint, status=status,
        ).inc()

        REQUEST_LATENCY.labels(
            service=service_name, method=method, endpoint=endpoint,
        ).observe(latency)

        if response.status_code >= 500:
            REQUEST_ERRORS.labels(service=service_name, endpoint=endpoint).inc()

        ACTIVE_REQUESTS.labels(service=service_name).dec()
        return response

    @app.teardown_request
    def teardown_request(exc):
        # Decrement active requests if after_request didn't run (e.g. exception)
        if exc is not None:
            ACTIVE_REQUESTS.labels(service=service_name).dec()

    logger.info('APM metrics enabled for service: %s  →  GET /metrics', service_name)
    return app


def _clean_endpoint(path: str) -> str:
    """Normalize dynamic path segments to avoid high-cardinality labels."""
    import re
    # Replace numeric IDs: /sessions/42/messages → /sessions/{id}/messages
    path = re.sub(r'/\d+', '/{id}', path)
    # Truncate very long paths
    return path[:80]
