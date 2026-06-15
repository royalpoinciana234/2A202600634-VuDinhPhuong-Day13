from __future__ import annotations

from collections import Counter
from statistics import mean

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []


def initialize_metrics_from_log() -> None:
    global TRAFFIC
    import json
    from pathlib import Path
    
    log_path = Path("data/logs.jsonl")
    if not log_path.exists():
        return
    try:
        with log_path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if data.get("service") == "api":
                        event = data.get("event")
                        if event == "response_sent":
                            TRAFFIC += 1
                            if "latency_ms" in data:
                                REQUEST_LATENCIES.append(int(data["latency_ms"]))
                            if "cost_usd" in data:
                                REQUEST_COSTS.append(float(data["cost_usd"]))
                            if "tokens_in" in data:
                                REQUEST_TOKENS_IN.append(int(data["tokens_in"]))
                            if "tokens_out" in data:
                                REQUEST_TOKENS_OUT.append(int(data["tokens_out"]))
                            quality = data.get("quality_score", 0.75)
                            QUALITY_SCORES.append(float(quality))
                        elif event == "request_failed":
                            error_type = data.get("error_type", "unknown")
                            ERRORS[error_type] += 1
                except Exception:
                    continue
    except Exception:
        pass


initialize_metrics_from_log()


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)



def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1



def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])



def snapshot() -> dict:
    return {
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
    }
