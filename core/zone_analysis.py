from data.market_data import fetch_candles
from core.zone_engine import detect_zones
from core.zone_monitor import monitor_zones
from core.zone_confirmation import confirm_zone
from core.risk_manager import calculate_trade_levels
from core.trading_mode import signals_allowed, get_mode
from core.signal_guard import is_new_signal
from core.signal_expiry import create_expiry


def run_zone_analysis():

    data = fetch_candles("M15")

    if not data["ok"]:
        return {
            "ok": False,
            "status": "NO TRADE",
            "reason": data["error"]
        }

    candles = data["candles"]
    zones = detect_zones(candles)

    if not zones["ok"]:
        return {
            "ok": False,
            "status": "NO TRADE",
            "reason": zones["error"]
        }

    monitor = monitor_zones(zones)

    if not monitor["ok"]:
        return {
            "ok": False,
            "status": "NO TRADE",
            "reason": monitor["error"]
        }

    if not signals_allowed():
        return {
            "ok": True,
            "price": zones["price"],
            "zone_alerts": monitor["alerts"],
            "confirmations": [],
            "status": "NO TRADE MODE",
            "reason": "SIGNALS ARE DISABLED"
        }

    confirmations = []

    all_zones = (
        zones["demand_zones"]
        + zones["supply_zones"]
    )

    for zone in all_zones:

        result = confirm_zone(
            candles,
            zone,
            zones["atr"]
        )

        if not result["confirmed"]:
            continue

        levels = calculate_trade_levels(
            candles,
            result["direction"]
        )

        if not levels["ok"]:
            continue

        signal = {
            "direction": result["direction"],
            "zone": zone
        }

        if not is_new_signal(signal):
            continue

        confirmations.append({
            "direction": result["direction"],
            "status": result["status"],
            "reason": result["reason"],
            "zone": zone,
            "levels": levels,
            "expiry": create_expiry(60)
        })

    return {
        "ok": True,
        "price": zones["price"],
        "zone_alerts": monitor["alerts"],
        "confirmations": confirmations,
        "status": (
            "CONFIRMED SETUP"
            if confirmations
            else "WAIT FOR CONFIRMATION"
        )
    }


if __name__ == "__main__":

    print("PROFX AI SIGNALS - ZONE ANALYSIS")

    mode = get_mode()
    print("TRADING MODE:", mode["mode"])

    result = run_zone_analysis()

    print("\nSTATUS:", result["status"])

    if not result["ok"]:
        print("REASON:", result["reason"])

    else:
        print("PRICE:", result["price"])

        print("\nZONE ALERTS:")
        for alert in result["zone_alerts"]:
            print(alert["type"], alert["zone"])

        print("\nCONFIRMATIONS:")

        for item in result["confirmations"]:
            print("\n", item["status"])
            print("DIRECTION:", item["direction"])
            print("REASON:", item["reason"])
            print("ZONE:", item["zone"])

            for key, value in item["levels"].items():
                print(key.upper() + ":", value)

            print("EXPIRY:", item["expiry"]["expires_at"])
