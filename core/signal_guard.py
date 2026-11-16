import json
import os
import hashlib

STATE_FILE = "data/signal_guard.json"


def load_state():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(STATE_FILE):
        return []

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_state(state):
    os.makedirs("data", exist_ok=True)

    temp_file = STATE_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)

    os.replace(temp_file, STATE_FILE)


def signal_key(signal):
    raw = "|".join([
        str(signal["direction"]),
        str(signal["zone"]["type"]),
        str(signal["zone"]["low"]),
        str(signal["zone"]["high"]),
        str(signal["zone"]["created_at"])
    ])

    return hashlib.sha256(raw.encode()).hexdigest()


def is_new_signal(signal):

    if signal.get("direction") not in ["BUY", "SELL"]:
        return False

    if "zone" not in signal:
        return False

    state = load_state()
    key = signal_key(signal)

    if key in state:
        return False

    state.append(key)

    # Iň soňky 500 signaly ýatda sakla
    state = state[-500:]

    save_state(state)

    return True


if __name__ == "__main__":

    test_signal = {
        "direction": "BUY",
        "zone": {
            "type": "DEMAND",
            "low": 3860,
            "high": 3865,
            "created_at": "TEST"
        }
    }

    print("FIRST:", is_new_signal(test_signal))
    print("SECOND:", is_new_signal(test_signal))
