import json
import yaml
from pathlib import Path
from statistics import mean

ALERT_RULES_PATH = Path("config/alert_rules.yaml")
LOGS_PATH = Path("data/logs.jsonl")


def calculate_percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def main() -> None:
    print("=== Alert Evaluation Test Script ===")

    # 1. Load alert rules
    if not ALERT_RULES_PATH.exists():
        print(f"Error: Alert rules file not found at {ALERT_RULES_PATH}")
        return

    with ALERT_RULES_PATH.open("r", encoding="utf-8") as f:
        rules_data = yaml.safe_load(f)

    alerts = rules_data.get("alerts", [])
    print(f"Loaded {len(alerts)} alert rules from {ALERT_RULES_PATH}:\n")
    for a in alerts:
        print(f" - [{a['name']}] Severity: {a['severity']} | Condition: {a['condition']}")

    # 2. Load and parse logs
    if not LOGS_PATH.exists():
        print(f"\nError: Logs file not found at {LOGS_PATH}. Run load tests first.")
        return

    print(f"\nAnalyzing logs from {LOGS_PATH}...")
    latencies = []
    costs = []
    success_count = 0
    fail_count = 0

    with LOGS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("service") == "api":
                    event = data.get("event")
                    if event == "response_sent":
                        success_count += 1
                        if "latency_ms" in data:
                            latencies.append(int(data["latency_ms"]))
                        if "cost_usd" in data:
                            costs.append(float(data["cost_usd"]))
                    elif event == "request_failed":
                        fail_count += 1
            except Exception:
                continue

    total_requests = success_count + fail_count
    if total_requests == 0:
        print("No API requests found in logs. Cannot evaluate alert conditions.")
        return

    # Calculate SLIs
    latency_p95 = calculate_percentile(latencies, 95)
    error_rate = (fail_count / total_requests) * 100
    total_cost = sum(costs)

    print("\n--- Current System SLIs ---")
    print(f"Total Requests: {total_requests}")
    print(f"Latency P95:    {latency_p95:.1f} ms")
    print(f"Error Rate:     {error_rate:.2f}% ({fail_count} failed, {success_count} success)")
    print(f"Total Cost:     ${total_cost:.4f} (across analyzed log period)")

    # 3. Evaluate Alerts
    print("\n--- Alert Evaluation Results ---")
    for a in alerts:
        name = a["name"]
        cond = a["condition"]
        firing = False
        details = ""

        if name == "high_latency_p95":
            # Rule: latency_p95_ms > 5000 for 30m (we'll check against current P95)
            firing = latency_p95 > 5000
            details = f"P95 latency is {latency_p95:.1f}ms (threshold: >5000ms)"
        elif name == "high_error_rate":
            # Rule: error_rate_pct > 5 for 5m
            firing = error_rate > 5
            details = f"Error rate is {error_rate:.2f}% (threshold: >5%)"
        elif name == "cost_budget_spike":
            # Rule: hourly_cost_usd > 2x_baseline for 15m
            # For testing, let's trigger it if the average request cost is higher than 0.005 USD
            avg_cost = mean(costs) if costs else 0.0
            firing = avg_cost > 0.005
            details = f"Avg cost per request is ${avg_cost:.6f} (baseline: $0.002000)"

        status = "\033[91m[FIRING]\033[0m" if firing else "\033[92m[OK]\033[0m"
        print(f"{status} {name}: {details}")
        print(f"  -> Runbook: {a['runbook']}")


if __name__ == "__main__":
    main()
