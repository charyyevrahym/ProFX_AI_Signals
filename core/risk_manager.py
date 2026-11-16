from strategies.indicators import calculate_indicators


def calculate_trade_levels(
    candles,
    direction,
    risk_reward_1=1.0,
    risk_reward_2=2.0,
    risk_reward_3=3.0,
    atr_multiplier=1.5
):

    if direction not in ["BUY", "SELL"]:
        return {
            "ok": False,
            "error": "INVALID DIRECTION"
        }

    try:
        indicators = calculate_indicators(candles)

        entry = indicators["price"]
        atr = indicators["atr"]

        if atr <= 0 or entry <= 0:
            return {
                "ok": False,
                "error": "INVALID PRICE OR ATR"
            }

        risk_distance = atr * atr_multiplier

        if direction == "BUY":
            stop_loss = entry - risk_distance

            tp1 = entry + risk_distance * risk_reward_1
            tp2 = entry + risk_distance * risk_reward_2
            tp3 = entry + risk_distance * risk_reward_3

        else:
            stop_loss = entry + risk_distance

            tp1 = entry - risk_distance * risk_reward_1
            tp2 = entry - risk_distance * risk_reward_2
            tp3 = entry - risk_distance * risk_reward_3

        return {
            "ok": True,
            "direction": direction,
            "entry": round(entry, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit_1": round(tp1, 2),
            "take_profit_2": round(tp2, 2),
            "take_profit_3": round(tp3, 2),
            "atr": round(atr, 4),
            "risk_distance": round(risk_distance, 4),
            "risk_reward": [1.0, 2.0, 3.0],
            "status": "CALCULATED - MANUAL REVIEW REQUIRED"
        }

    except (ValueError, KeyError, TypeError) as error:
        return {
            "ok": False,
            "error": str(error)
        }


if __name__ == "__main__":

    from data.market_data import fetch_candles

    print("PROFX AI SIGNALS - RISK MANAGER TEST")

    data = fetch_candles("M15")

    if not data["ok"]:
        print("DATA ERROR:", data["error"])

    else:
        result = calculate_trade_levels(
            data["candles"],
            "BUY"
        )

        if result["ok"]:
            for key, value in result.items():
                print(key.upper() + ":", value)
        else:
            print("RISK ERROR:", result["error"])
