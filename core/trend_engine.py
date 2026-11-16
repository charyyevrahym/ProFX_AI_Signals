from data.market_data import fetch_candles
from strategies.indicators import calculate_indicators


def analyze_timeframe(timeframe):

    data = fetch_candles(timeframe)

    if not data["ok"]:
        return {
            "ok": False,
            "timeframe": timeframe,
            "error": data["error"]
        }

    try:
        indicators = calculate_indicators(data["candles"])

        price = indicators["price"]
        ema50 = indicators["ema_50"]
        ema200 = indicators["ema_200"]
        rsi = indicators["rsi"]

        if ema50 > ema200 and price > ema50 and rsi > 50:
            trend = "BULLISH"

        elif ema50 < ema200 and price < ema50 and rsi < 50:
            trend = "BEARISH"

        else:
            trend = "NEUTRAL"

        return {
            "ok": True,
            "timeframe": timeframe,
            "trend": trend,
            "price": price,
            "ema50": ema50,
            "ema200": ema200,
            "rsi": rsi,
            "atr": indicators["atr"]
        }

    except (ValueError, KeyError, TypeError) as error:
        return {
            "ok": False,
            "timeframe": timeframe,
            "error": str(error)
        }


def analyze_market():

    timeframes = ["H4", "H1", "M15", "M5"]

    results = {}

    for timeframe in timeframes:
        results[timeframe] = analyze_timeframe(timeframe)

    failed = [
        tf for tf, result in results.items()
        if not result["ok"]
    ]

    if failed:
        return {
            "status": "NO TRADE",
            "reason": "DATA ERROR: " + ", ".join(failed),
            "timeframes": results
        }

    trends = [
        results[tf]["trend"]
        for tf in timeframes
    ]

    if all(trend == "BULLISH" for trend in trends):
        status = "BULLISH ALIGNMENT"

    elif all(trend == "BEARISH" for trend in trends):
        status = "BEARISH ALIGNMENT"

    else:
        status = "WAIT FOR CONFIRMATION"

    return {
        "status": status,
        "timeframes": results
    }


if __name__ == "__main__":

    print("PROFX AI SIGNALS - MULTI TIMEFRAME ANALYSIS")

    market = analyze_market()

    print("\nMARKET STATUS:", market["status"])

    if "reason" in market:
        print("REASON:", market["reason"])

    for timeframe, result in market["timeframes"].items():

        print("\n", timeframe)

        if result["ok"]:
            print("TREND:", result["trend"])
            print("PRICE:", result["price"])
            print("RSI:", round(result["rsi"], 2))
        else:
            print("ERROR:", result["error"])/o

