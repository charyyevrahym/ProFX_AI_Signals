from strategies.indicators import calculate_indicators


def ema_strategy(ind):
    if ind["ema_50"] > ind["ema_200"] and ind["price"] > ind["ema_50"]:
        return "BUY"
    if ind["ema_50"] < ind["ema_200"] and ind["price"] < ind["ema_50"]:
        return "SELL"
    return "NEUTRAL"


def rsi_strategy(ind):
    if ind["rsi"] < 30:
        return "POTENTIAL BUY"
    if ind["rsi"] > 70:
        return "POTENTIAL SELL"
    return "NEUTRAL"


def atr_strategy(ind):
    if ind["atr"] <= 0:
        return "INVALID"
    return "VOLATILITY OK"


def vwap_strategy(ind):
    if ind["vwap"] is None:
        return "UNAVAILABLE"
    if ind["price"] > ind["vwap"]:
        return "BUY"
    if ind["price"] < ind["vwap"]:
        return "SELL"
    return "NEUTRAL"


def support_resistance_strategy(candles, lookback=50):
    recent = candles[-lookback:]

    support = min(c["low"] for c in recent)
    resistance = max(c["high"] for c in recent)
    price = candles[-1]["close"]

    if price <= support * 1.001:
        signal = "NEAR SUPPORT"
    elif price >= resistance * 0.999:
        signal = "NEAR RESISTANCE"
    else:
        signal = "BETWEEN ZONES"

    return {
        "signal": signal,
        "support": support,
        "resistance": resistance
    }


def crt_strategy(candles):
    if len(candles) < 3:
        return "INSUFFICIENT DATA"

    previous = candles[-2]
    current = candles[-1]

    if (
        current["low"] < previous["low"]
        and current["close"] > previous["low"]
        and current["close"] < previous["high"]
    ):
        return "POTENTIAL BULLISH CRT"

    if (
        current["high"] > previous["high"]
        and current["close"] < previous["high"]
        and current["close"] > previous["low"]
    ):
        return "POTENTIAL BEARISH CRT"

    return "NO CRT SETUP"


def smc_strategy(candles):
    if len(candles) < 20:
        return "INSUFFICIENT DATA"

    previous = candles[-2]
    current = candles[-1]

    if current["close"] > previous["high"]:
        return "POTENTIAL BULLISH BREAK"

    if current["close"] < previous["low"]:
        return "POTENTIAL BEARISH BREAK"

    return "NO CLEAR STRUCTURE BREAK"


def opening_range_strategy(candles, lookback=12):
    if len(candles) < lookback + 1:
        return "INSUFFICIENT DATA"

    opening = candles[-(lookback + 1):-1]

    high = max(c["high"] for c in opening)
    low = min(c["low"] for c in opening)
    price = candles[-1]["close"]

    if price > high:
        return "POTENTIAL BREAKOUT BUY"

    if price < low:
        return "POTENTIAL BREAKOUT SELL"

    return "INSIDE OPENING RANGE"


def analyze_strategies(candles):

    ind = calculate_indicators(candles)

    results = {
        "SMC": smc_strategy(candles),
        "CRT": crt_strategy(candles),
        "EMA 50/200": ema_strategy(ind),
        "VWAP": vwap_strategy(ind),
        "RSI DIVERGENCE": rsi_strategy(ind),
        "ATR": atr_strategy(ind),
        "OPENING RANGE BREAKOUT": opening_range_strategy(candles),
        "SUPPORT RESISTANCE": support_resistance_strategy(candles)
    }

    return {
        "price": ind["price"],
        "indicators": ind,
        "strategies": results,
        "status": "WAIT FOR CONFIRMATION"
    }


if __name__ == "__main__":

    from data.market_data import fetch_candles

    print("PROFX AI SIGNALS - STRATEGY TEST")

    data = fetch_candles("M15")

    if not data["ok"]:
        print("DATA ERROR:", data["error"])
    else:
        result = analyze_strategies(data["candles"])

        print("PRICE:", result["price"])
        print("\nSTRATEGY RESULTS:")

        for name, value in result["strategies"].items():
            print(name + ":", value)

        print("\nSTATUS:", result["status"])
