import os
import requests

from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from config.settings import SYMBOL, TIMEFRAMES, REQUEST_TIMEOUT

load_dotenv()

API_KEY = os.getenv("TWELVE_DATA_API_KEY")
API_URL = "https://api.twelvedata.com/time_series"


def fetch_candles(timeframe="M15", outputsize=220):

    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        return {"ok": False, "error": "API KEY NOT FOUND"}

    if timeframe not in TIMEFRAMES:
        return {"ok": False, "error": "INVALID TIMEFRAME"}

    params = {
        "symbol": SYMBOL,
        "interval": TIMEFRAMES[timeframe],
        "outputsize": outputsize + 2,
        "apikey": API_KEY,
        "format": "JSON",
        "timezone": "UTC"
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        if "values" not in data:
            return {
                "ok": False,
                "error": data.get("message", "NO MARKET DATA")
            }

        candles = []

        for item in reversed(data["values"]):
            candle = {
                "datetime": item["datetime"],
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": float(item.get("volume") or 0)
            }

            if (
                candle["low"] <= 0
                or candle["high"] < candle["low"]
                or candle["high"] < max(
                    candle["open"], candle["close"]
                )
                or candle["low"] > min(
                    candle["open"], candle["close"]
                )
            ):
                continue

            candles.append(candle)

        if len(candles) < 50:
            return {
                "ok": False,
                "error": "INSUFFICIENT VALID CANDLES"
            }

        # Closed-candle filtering
        now = datetime.now(timezone.utc)

        interval_minutes = {
            "M5": 5,
            "M15": 15,
            "H1": 60,
            "H4": 240
        }

        minutes = interval_minutes[timeframe]
        closed_candles = []

        for candle in candles:
            candle_time = datetime.strptime(
                candle["datetime"],
                "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)

            candle_end = candle_time + timedelta(
                minutes=minutes
            )

            if candle_end <= now:
                closed_candles.append(candle)

        if len(closed_candles) < 50:
            return {
                "ok": False,
                "error": "NOT ENOUGH CLOSED CANDLES"
            }

        latest_time = datetime.strptime(
            closed_candles[-1]["datetime"],
            "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)

        age_minutes = (
            now - (latest_time + timedelta(minutes=minutes))
        ).total_seconds() / 60

        if age_minutes > max(minutes * 3, 30):
            return {
                "ok": False,
                "error": "MARKET DATA IS STALE"
            }

        return {
            "ok": True,
            "symbol": SYMBOL,
            "timeframe": timeframe,
            "count": len(closed_candles),
            "latest_candle": closed_candles[-1]["datetime"],
            "price": closed_candles[-1]["close"],
            "age_minutes": round(age_minutes, 1),
            "candles": closed_candles[-outputsize:]
        }

    except requests.exceptions.RequestException:
        return {"ok": False, "error": "NETWORK/SSL CONNECTION ERROR"}

    except (ValueError, KeyError, TypeError) as error:
        return {"ok": False, "error": str(error)}


if __name__ == "__main__":

    print("PROFX AI SIGNALS - GOLD DATA TEST")

    result = fetch_candles("M15")

    if result["ok"]:
        print("DATA READY")
        print("SYMBOL:", result["symbol"])
        print("TIMEFRAME:", result["timeframe"])
        print("CLOSED CANDLES:", result["count"])
        print("LATEST CLOSED:", result["latest_candle"])
        print("PRICE:", result["price"])
        print("DATA AGE:", result["age_minutes"], "minutes")
    else:
        print("DATA ERROR:", result["error"])

