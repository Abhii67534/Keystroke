import pandas as pd

def extract_features(events):
    """
    Expects a list of dicts with:
    {
      "key": "a",
      "down": 123456789,
      "up": 123456900
    }
    Returns a DataFrame with numeric timing features.
    """
    features = []

    for i in range(1, len(events)):
        prev = events[i - 1]
        curr = events[i]

        # Individual key hold times
        prev_hold = prev["up"] - prev["down"]
        curr_hold = curr["up"] - curr["down"]

        # Between-key timings
        down_down = curr["down"] - prev["down"]
        up_down = curr["down"] - prev["up"]
        up_up = curr["up"] - prev["up"]
        down_up = curr["up"] - prev["down"]
        inter_key_total = curr["up"] - prev["down"]

        features.append({
            "prev_hold_time": prev_hold,
            "curr_hold_time": curr_hold,
            "down_down": down_down,
            "up_down": up_down,
            "up_up": up_up,
            "down_up": down_up,
            "inter_key_total_time": inter_key_total
        })

    return pd.DataFrame(features)
