from core.trend_engine import analyze_market
from strategies.strategy_engine import analyze_strategies
from data.market_data import fetch_candles


def build_signal():

    market = analyze_market()

    if market["status"] not in [
        "BULLISH ALIGNMENT",
        "BEARISH ALIGNMENT"
    ]:
        return {
            "status": "WAIT FOR CONFIRMATION",
            "reason": "TIMEFRAME ALIGNMENT NOT CONFIRMED"
        }

    data = fetch_candles("M15")

    if not data["ok"]:
        return {
            "status": "NO TRADE",
            "reason": data["error"]
        }

    analysis = analyze_strategies(data["candles"])
    strategies = analysis["strategies"]

    direction = (
        "BUY"
        if market["status"] == "BULLISH ALIGNMENT"
        else "SELL"
    )

    confirmations = []

    if strategies["EMA 50/200"] == direction:
        confirmations.append("EMA 50/200")

    if direction == "BUY" and strategies["RSI DIVERGENCE"] == "POTENTIAL BUY":
        confirmations.append("RSI")

    if direction == "SELL" and strategies["RSI DIVERGENCE"] == "POTENTIAL SELL":
        confirmations.append("RSI")

    if direction == "BUY" and strategies["SMC"] == "POTENTIAL BULLISH BREAK":
        confirmations.append("SMC")

    if direction == "SELL" and strategies["SMC"] == "POTENTIAL BEARISH BREAK":
        confirmations.append("SMC")

    if direction == "BUY" and strategies["CRT"] == "POTENTIAL BULLISH CRT":
        confirmations.append("CRT")

    if direction == "SELL" and strategies["CRT"] == "POTENTIAL BEARISH CRT":
        confirmations.append("CRT")

    if len(confirmations) < 3:
        return {
            "status": "WAIT FOR CONFIRMATION",
            "direction": direction,
            "confirmations": confirmations,
            "reason": "NOT ENOUGH STRATEGY CONFIRMATIONS"
        }

    return {
        "status": "SETUP DETECTED - MANUAL REVIEW REQUIRED",
        "direction": direction,
        "price": analysis["price"],
        "confirmations": confirmations,
        "reason": "PRELIMINARY CONDITIONS MET"
    }


if __name__ == "__main__":

    print("PROFX AI SIGNALS - SIGNAL ENGINE")

    result = build_signal()

    print("\nSTATUS:", result["status"])

    if "direction" in result:
        print("DIRECTION:", result["direction"])

    if "price" in result:
        print("PRICE:", result["price"])

    if "confirmations" in result:
        print("CONFIRMATIONS:", result["confirmations"])

    print("REASON:", result["reason"])
