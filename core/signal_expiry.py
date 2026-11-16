from datetime import datetime, timezone, timedelta


def create_expiry(expiry_minutes=60):

    if expiry_minutes <= 0:
        raise ValueError("EXPIRY MUST BE POSITIVE")

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=expiry_minutes
    )

    return {
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "expiry_minutes": expiry_minutes,
        "status": "ACTIVE"
    }


def check_expiry(signal):

    try:
        expires_at = datetime.fromisoformat(
            signal["expires_at"]
        )

        if expires_at.tzinfo is None:
            return {
                "expired": True,
                "status": "INVALID EXPIRY TIME"
            }

        now = datetime.now(timezone.utc)

        if now >= expires_at:
            return {
                "expired": True,
                "status": "EXPIRED"
            }

        remaining = (
            expires_at - now
        ).total_seconds() / 60

        return {
            "expired": False,
            "status": "ACTIVE",
            "remaining_minutes": round(remaining, 1)
        }

    except (KeyError, ValueError, TypeError):
        return {
            "expired": True,
            "status": "INVALID SIGNAL EXPIRY"
        }


if __name__ == "__main__":

    signal = create_expiry(60)

    print("SIGNAL EXPIRY TEST")
    print("CREATED:", signal["created_at"])
    print("EXPIRES:", signal["expires_at"])

    result = check_expiry(signal)

    print("STATUS:", result["status"])
    print("REMAINING:", result.get("remaining_minutes"))
