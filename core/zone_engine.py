from strategies.indicators import calculate_indicators


def detect_zones(candles, lookback=100):

    if len(candles) < 30:
        return {
            "ok": False,
            "error": "NOT ENOUGH CANDLES"
        }

    recent = candles[-lookback:]
    indicators = calculate_indicators(candles)
    atr = indicators["atr"]
    price = candles[-1]["close"]

    if atr <= 0:
        return {
            "ok": False,
            "error": "INVALID ATR"
        }

    demand_zones = []
    supply_zones = []

    start = max(2, len(recent) - 60)
    end = len(recent) - 2

    for i in range(start, end):

        previous = recent[i - 1]
        current = recent[i]
        following = recent[i + 1]

        body = abs(current["close"] - current["open"])

        # DEMAND ZONE: swing low + upward movement
        if (
            current["low"] < previous["low"]
            and current["low"] < following["low"]
            and following["close"] > current["high"]
            and body >= atr * 0.10
        ):
            zone = {
                "type": "DEMAND",
                "low": round(current["low"], 2),
                "high": round(
                    max(current["open"], current["close"]), 2
                ),
                "created_at": current["datetime"]
            }

            if zone["high"] > zone["low"]:
                demand_zones.append(zone)

        # SUPPLY ZONE: swing high + downward movement
        if (
            current["high"] > previous["high"]
            and current["high"] > following["high"]
            and following["close"] < current["low"]
            and body >= atr * 0.10
        ):
            zone = {
                "type": "SUPPLY",
                "low": round(
                    min(current["open"], current["close"]), 2
                ),
                "high": round(current["high"], 2),
                "created_at": current["datetime"]
            }

            if zone["high"] > zone["low"]:
                supply_zones.append(zone)

    # Duplicate zones are removed
    def remove_duplicates(zones):
        unique = []

        for zone in zones:
            duplicate = any(
                abs(zone["low"] - old["low"]) < atr * 0.20
                and abs(zone["high"] - old["high"]) < atr * 0.20
                for old in unique
            )

            if not duplicate:
                unique.append(zone)

        return unique

    demand_zones = remove_duplicates(demand_zones)
    supply_zones = remove_duplicates(supply_zones)

    return {
        "ok": True,
        "price": price,
        "atr": round(atr, 4),
        "demand_zones": demand_zones,
        "supply_zones": supply_zones
    }


def check_zone_status(price, zone, atr):

    distance = min(
        abs(price - zone["low"]),
        abs(price - zone["high"])
    )

    if zone["low"] <= price <= zone["high"]:
        return "ENTERED ZONE"

    if distance <= atr * 0.50:
        return "APPROACHING ZONE"

    return "OUTSIDE ZONE"


if __name__ == "__main__":

    from data.market_data import fetch_candles

    print("PROFX AI SIGNALS - ZONE ENGINE TEST")

    data = fetch_candles("M15")

    if not data["ok"]:
        print("DATA ERROR:", data["error"])

    else:
        result = detect_zones(data["candles"])

        if not result["ok"]:
            print("ZONE ERROR:", result["error"])

        else:
            print("PRICE:", result["price"])
            print("ATR:", result["atr"])

            print("\nDEMAND ZONES:")
            for zone in result["demand_zones"]:
                print(zone)

            print("\nSUPPLY ZONES:")
            for zone in result["supply_zones"]:
                print(zone)

            print("\nZONE ENGINE: READY")
