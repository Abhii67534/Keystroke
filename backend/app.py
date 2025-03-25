from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
from analyze import extract_features
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean

app = Flask(__name__)
CORS(app)

USER_DIR = "users"
os.makedirs(USER_DIR, exist_ok=True)

@app.route("/enroll", methods=["POST"])
def enroll_user():
    data = request.get_json()
    username = data.get("username")
    sessions = data.get("sessions")  # List of keystroke lists

    if not username or not sessions:
        return jsonify({"error": "Missing username or sessions"}), 400

    all_features = []
    for keystrokes in sessions:
        features = extract_features(keystrokes)
        if not features.empty:
            avg = features.mean().to_dict()
            all_features.append(avg)

    df = pd.DataFrame(all_features)
    path = os.path.join(USER_DIR, f"{username}.csv")
    df.to_csv(path, index=False)

    return jsonify({"status": "enrolled", "samples": len(df), "user": username})


@app.route("/verify", methods=["POST"])
def verify_user():
    data = request.get_json()
    username = data.get("username")
    keystrokes = data.get("keystrokes")

    if not username or not keystrokes:
        return jsonify({"error": "Missing username or keystrokes"}), 400

    path = os.path.join(USER_DIR, f"{username}.csv")
    if not os.path.exists(path):
        return jsonify({"error": "User not found"}), 404

    df_user = pd.read_csv(path)
    current_features = extract_features(keystrokes)
    if current_features.empty:
        return jsonify({"error": "Invalid typing session"}), 400

    profile_mean = df_user.mean().values
    input_mean = current_features.mean().values

    cosine_sim = cosine_similarity([profile_mean], [input_mean])[0][0]
    eu_dist = euclidean(profile_mean, input_mean)

    # 🔐 Combined decision rule
    COS_THRESHOLD = 0.90
    EUC_THRESHOLD = 50  # Tune this

    is_genuine = cosine_sim >= COS_THRESHOLD and eu_dist <= EUC_THRESHOLD

    return jsonify({
        "prediction": "genuine" if is_genuine else "impostor",
        "cosine_similarity": round(cosine_sim, 4),
        "euclidean_distance": round(eu_dist, 2)
    })


if __name__ == "__main__":
    app.run(debug=True)
