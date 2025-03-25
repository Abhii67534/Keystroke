import pandas as pd

def extract_features(events):
    """
    Expects a list of dicts with:
    {
      "key": "a",
      "down": 123456789,
      "up": 123456900
    }
    """
    features = []

    for i in range(1, len(events)):
        prev = events[i - 1]
        curr = events[i]

        hold_time = curr["up"] - curr["down"]
        flight_time = curr["down"] - prev["down"]  # Down–Down time
        latency = curr["down"] - prev["up"]        # Up–Down (between keys)

        features.append({
            "hold_time": hold_time,
            "flight_time": flight_time,
            "latency": latency
        })

    return pd.DataFrame(features)
