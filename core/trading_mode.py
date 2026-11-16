import json
import os

MODE_FILE = "data/trading_mode.json"


def save_mode(no_trade=True):

    os.makedirs("data", exist_ok=True)

    data = {
        "no_trade": bool(no_trade),
        "mode": "NO TRADE" if no_trade else "SIGNALS"
    }

    temp_file = MODE_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    os.replace(temp_file, MODE_FILE)

    return data


def get_mode():

    if not os.path.exists(MODE_FILE):
        return save_mode(True)

    try:
        with open(MODE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        no_trade = data.get("no_trade", True)

        return {
            "no_trade": bool(no_trade),
            "mode": "NO TRADE" if no_trade else "SIGNALS"
        }

    except (json.JSONDecodeError, OSError):
        return save_mode(True)


def signals_allowed():
    return not get_mode()["no_trade"]


if __name__ == "__main__":

    print("PROFX AI SIGNALS - TRADING MODE TEST")

    save_mode(True)

    print("CURRENT MODE:", get_mode()["mode"])
    print("SIGNALS ALLOWED:", signals_allowed())

    save_mode(False)

    print("CHANGED MODE:", get_mode()["mode"])
    print("SIGNALS ALLOWED:", signals_allowed())

    save_mode(True)

    print("FINAL MODE:", get_mode()["mode"])
