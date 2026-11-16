import json
import os

from datetime import datetime, timezone


HISTORY_FILE = "logs/signal_history.json"


def ensure_storage():
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump([], file)


def save_signal(signal):
    ensure_storage()

    history = load_history()

    record = {
        "id": len(history) + 1,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "symbol": signal.get("symbol", "XAU/USD"),
        "direction": signal.get("direction"),
        "entry": signal.get("entry"),
        "stop_loss": signal.get("stop_loss"),
        "take_profit_1": signal.get("take_profit_1"),
        "take_profit_2": signal.get("take_profit_2"),
        "take_profit_3": signal.get("take_profit_3"),
        "status": signal.get("status", "PENDING"),
        "result": "NOT RECORDED"
    }

    history.append(record)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)

    return record


def load_history():
    ensure_storage()

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def update_signal_result(signal_id, result):
    allowed = ["WIN", "LOSS", "BREAKEVEN", "CANCELLED"]

    if result not in allowed:
        return False

    history = load_history()

    for signal in history:
        if signal["id"] == signal_id:
            signal["result"] = result

            with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                json.dump(history, file, indent=4)

            return True

    return False


def signal_statistics():
    history = load_history()

    completed = [
        item for item in history
        if item["result"] in ["WIN", "LOSS", "BREAKEVEN"]
    ]

    wins = sum(
        item["result"] == "WIN" for item in completed
    )

    losses = sum(
        item["result"] == "LOSS" for item in completed
    )

    total = len(completed)

    win_rate = (
        round(wins / total * 100, 2)
        if total else 0
    )

    return {
        "total_signals": len(history),
        "completed": total,
        "wins": wins,
        "losses": losses,
        "win_rate_percent": win_rate
    }


if __name__ == "__main__":

    print("PROFX AI SIGNALS - HISTORY TEST")

    test_signal = {
        "symbol": "XAU/USD",
        "direction": "BUY",
        "entry": 3859.16,
        "stop_loss": 3845.32,
        "take_profit_1": 3873.00,
        "take_profit_2": 3886.84,
        "take_profit_3": 3900.68,
        "status": "TEST ONLY"
    }

    saved = save_signal(test_signal)

    print("SAVED:", saved["id"])
    print("TOTAL:", signal_statistics()["total_signals"])
    print("HISTORY FILE:", HISTORY_FILE)
