import pandas as pd
import numpy as np


def prepare_dataframe(candles):
    """Şem maglumatlaryny DataFrame görnüşine geçirýär."""

    if not candles or len(candles) < 50:
        raise ValueError("NOT ENOUGH CANDLES")

    df = pd.DataFrame(candles)

    required = ["open", "high", "low", "close", "volume"]

    for column in required:
        if column not in df.columns:
            raise ValueError(f"MISSING COLUMN: {column}")

        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    df = df.dropna(subset=required).reset_index(drop=True)

    if len(df) < 50:
        raise ValueError("NOT ENOUGH VALID CANDLES")

    return df


def calculate_ema(df, period):
    return df["close"].ewm(
        span=period,
        adjust=False,
        min_periods=period
    ).mean()


def calculate_rsi(df, period=14):
    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.mask(
        (avg_loss == 0) & (avg_gain > 0), 100
    )

    rsi = rsi.mask(
        (avg_gain == 0) & (avg_loss > 0), 0
    )

    rsi = rsi.mask(
        (avg_gain == 0) & (avg_loss == 0), 50
    )

    return rsi


def calculate_atr(df, period=14):
    previous_close = df["close"].shift(1)

    ranges = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - previous_close).abs(),
            (df["low"] - previous_close).abs()
        ],
        axis=1
    )

    true_range = ranges.max(axis=1)

    return true_range.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()


def calculate_vwap(df):
    typical_price = (
        df["high"] + df["low"] + df["close"]
    ) / 3

    volume = df["volume"].fillna(0)

    # Her bir UTC günü üçin aýratyn VWAP
    dates = pd.to_datetime(
        df["datetime"], utc=True
    ).dt.date

    weighted_price = typical_price * volume

    cumulative_price = weighted_price.groupby(
        dates
    ).cumsum()

    cumulative_volume = volume.groupby(
        dates
    ).cumsum()

    vwap = cumulative_price / cumulative_volume.replace(
        0, np.nan
    )

    return vwap


def calculate_indicators(candles):
    df = prepare_dataframe(candles)

    df["EMA_50"] = calculate_ema(df, 50)
    df["EMA_200"] = calculate_ema(df, 200)
    df["RSI_14"] = calculate_rsi(df, 14)
    df["ATR_14"] = calculate_atr(df, 14)
    df["VWAP"] = calculate_vwap(df)

    latest = df.iloc[-1]

    result = {
        "price": float(latest["close"]),
        "ema_50": float(latest["EMA_50"]),
        "ema_200": float(latest["EMA_200"]),
        "rsi": float(latest["RSI_14"]),
        "atr": float(latest["ATR_14"]),
        "vwap": (
            float(latest["VWAP"])
            if pd.notna(latest["VWAP"])
            else None
        )
    }

    for name, value in result.items():
        if value is not None and not np.isfinite(value):
            raise ValueError(f"INVALID INDICATOR: {name}")

    return result
