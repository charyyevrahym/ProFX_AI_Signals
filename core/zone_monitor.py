import json
import os

from core.zone_engine import check_zone_status


STATE_FILE = "data/zone_alert_state.json"


def load_state():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state):
    os.makedirs("data", exist_ok=True)

    temporary_file = STATE_FILE + ".tmp"

    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)

    os.replace(temporary_file, STATE_FILE)


def zone_key(zone):
    return (
        zone["type"]
        + "_"
        + str(zone["low"])
        + "_"
        + str(zone["high"])
        + "_"
        + zone["created_at"]
    )


def monitor_zones(zone_data):

    if not zone_data.get("ok"):
        return {
            "ok": False,
            "error": "INVALID ZONE DATA",
            "alerts": []
        }

    price = zone_data["price"]
    atr = zone_data["atr"]

    if atr <= 0:
        return {
            "ok": False,
            "error": "INVALID ATR",
            "alerts": []
        }

    state = load_state()
    alerts = []

    all_zones = (
        zone_data["demand_zones"]
        + zone_data["supply_zones"]
    )

    active_keys = set()

    for zone in all_zones:

        key = zone_key(zone)
        active_keys.add(key)

        current_status = check_zone_status(
            price, zone, atr
        )

        previous_status = state.get(key, "OUTSIDE ZONE")

        if current_status == "APPROACHING ZONE":

            if previous_status in [
                "OUTSIDE ZONE",
                "LEFT ZONE"
            ]:
                alerts.append({
                    "type": "APPROACHING ZONE",
                    "zone": zone,
                    "price": price
                })

        elif current_status == "ENTERED ZONE":

            if previous_status != "ENTERED ZONE":
                alerts.append({
                    "type": "ENTERED ZONE - WAIT FOR CONFIRMATION",
                    "zone": zone,
                    "price": price
                })

        elif previous_status == "ENTERED ZONE":
            alerts.append({
                "type": "LEFT ZONE",
                "zone": zone,
                "price": price
            })

        state[key] = current_status

    # Köne zolaklaryň ýagdaýyny arassalamak
    state = {
        key: value
        for key, value in state.items()
        if key in active_keys
    }

    save_state(state)

    return {
        "ok": True,
        "price": price,
        "alerts": alerts,
        "alert_count": len(alerts)
    }


if __name__ == "__main__":

    from data.market_data import fetch_candles
    from core.zone_engine import detect_zones

    print("PROFX AI SIGNALS - ZONE MONITOR TEST")

    data = fetch_candles("M15")

    if not data["ok"]:
        print("DATA ERROR:", data["error"])

    else:
        zones = detect_zones(data["candles"])
        result = monitor_zones(zones)

        if not result["ok"]:
            print("MONITOR ERROR:", result["error"])
        else:
            print("PRICE:", result["price"])
            print("ALERT COUNT:", result["alert_count"])

            for alert in result["alerts"]:
                print("\nALERT:", alert["type"])
                print("ZONE:", alert["zone"])
                print("PRICE:", alert["price"])

            print("\nZONE MONITOR: READY")
