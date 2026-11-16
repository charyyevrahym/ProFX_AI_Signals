def confirm_zone(candles, zone, atr):

    if len(candles) < 2 or atr <= 0:
        return {
            "confirmed": False,
            "status": "WAIT FOR CONFIRMATION",
            "reason": "INSUFFICIENT DATA"
        }

    previous = candles[-2]
    current = candles[-1]

    body = abs(current["close"] - current["open"])

    if body < atr * 0.20:
        return {
            "confirmed": False,
            "status": "WAIT FOR CONFIRMATION",
            "reason": "CANDLE BODY TOO SMALL"
        }

    if zone["type"] == "DEMAND":

        touched = (
            previous["low"] <= zone["high"]
            and previous["high"] >= zone["low"]
        )

        bullish = (
            current["close"] > current["open"]
            and current["close"] > zone["high"]
        )

        if touched and bullish:
            return {
                "confirmed": True,
                "direction": "BUY",
                "status": "CONFIRMED BUY",
                "reason": "BULLISH DEMAND REJECTION"
            }

    elif zone["type"] == "SUPPLY":

        touched = (
            previous["high"] >= zone["low"]
            and previous["low"] <= zone["high"]
        )

        bearish = (
            current["close"] < current["open"]
            and current["close"] < zone["low"]
        )

        if touched and bearish:
            return {
                "confirmed": True,
                "direction": "SELL",
                "status": "CONFIRMED SELL",
                "reason": "BEARISH SUPPLY REJECTION"
            }

    return {
        "confirmed": False,
        "status": "WAIT FOR CONFIRMATION",
        "reason": "NO VALID REJECTION"
    }
