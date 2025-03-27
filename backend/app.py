from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
from analyze import extract_features
from networkfeatures import extract_network_features
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

USER_DIR = "users"
os.makedirs(USER_DIR, exist_ok=True)

# -------------------- ENROLL KEYSTROKES -------------------- #
@app.route("/enroll", methods=["POST"])
def enroll_user():
    data = request.get_json()
    username = data.get("username")
    sessions = data.get("sessions")

    if not username or not sessions:
        return jsonify({"error": "Missing username or sessions"}), 400

    all_features = []
    for keystrokes in sessions:
        features = extract_features(keystrokes)
        if not features.empty:
            avg = features.mean().to_dict()
            avg["timestamp"] = datetime.now(timezone.utc).isoformat()
            all_features.append(avg)

    df = pd.DataFrame(all_features)
    path = os.path.join(USER_DIR, f"{username}.csv")
    if os.path.exists(path):
        df_old = pd.read_csv(path)
        df = pd.concat([df_old, df], ignore_index=True)

    df.to_csv(path, index=False)

    return jsonify({"status": "enrolled", "samples": len(df), "user": username})

# -------------------- ENROLL NETWORK BEHAVIOR -------------------- #
@app.route("/network-enroll", methods=["POST"])
def enroll_network():
    data = request.get_json()
    username = data.get("username")
    session = data.get("network_session")

    if not username or not session:
        return jsonify({"error": "Missing username or network data"}), 400

    features = extract_network_features(session)
    if not isinstance(features, dict):
        features = dict(zip(["session_duration", "avg_packet_size", "total_packets", "dns_queries", "http_ratio", "https_ratio"], features))

    features["timestamp"] = datetime.now(timezone.utc).isoformat()

    df = pd.DataFrame([features], columns=[
        "session_duration", "avg_packet_size", "total_packets",
        "dns_queries", "http_ratio", "https_ratio", "timestamp"
    ])

    path = os.path.join(USER_DIR, f"{username}_network.csv")
    if os.path.exists(path):
        old = pd.read_csv(path)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(path, index=False)
    return jsonify({"status": "network session enrolled"})

# -------------------- USER DATA FOR CHART -------------------- #
@app.route("/user-data/<username>", methods=["GET"])
def get_user_data(username):
    path_key = os.path.join(USER_DIR, f"{username}.csv")
    path_net = os.path.join(USER_DIR, f"{username}_network.csv")

    if not os.path.exists(path_key) or not os.path.exists(path_net):
        return jsonify({"error": "User data not found"}), 404

    df_key = pd.read_csv(path_key)
    df_net = pd.read_csv(path_net)

    if "timestamp" not in df_key.columns or "timestamp" not in df_net.columns:
        return jsonify({"error": "Timestamp missing in user data"}), 500

    return jsonify({
        "keystroke": {
            "timestamps": df_key["timestamp"].tolist(),
            "hold_time": df_key["curr_hold_time"].tolist() if "curr_hold_time" in df_key.columns else []
        },
        "network": {
            "timestamps": df_net["timestamp"].tolist(),
            "avg_packet_size": df_net["avg_packet_size"].tolist() if "avg_packet_size" in df_net.columns else []
        }
    })

# -------------------- VERIFY COMBINED BIOMETRICS -------------------- #
@app.route("/verify", methods=["POST"])
def verify_user():
    try:
        data = request.get_json()
        username = data.get("username")
        keystrokes = data.get("keystrokes")
        net_session = data.get("network_session")

        if not username or not keystrokes or not net_session:
            return jsonify({"error": "Missing username, keystrokes, or network session"}), 400

        key_path = os.path.join(USER_DIR, f"{username}.csv")
        if not os.path.exists(key_path):
            return jsonify({"error": "Keystroke profile not found"}), 404

        df_user = pd.read_csv(key_path)
        current_features = extract_features(keystrokes)
        if current_features.empty:
            return jsonify({"error": "Invalid typing session"}), 400

        profile_mean = df_user.drop(columns=["timestamp"]).mean().values
        input_mean = current_features.mean().values

        cosine_sim = cosine_similarity([profile_mean], [input_mean])[0][0]
        eu_dist = euclidean(profile_mean, input_mean)

        net_path = os.path.join(USER_DIR, f"{username}_network.csv")
        if not os.path.exists(net_path):
            return jsonify({"error": "Network profile not found"}), 404

        net_df = pd.read_csv(net_path)
        net_profile = net_df.drop(columns=["timestamp"]).mean().values
        net_input = extract_network_features(net_session)

        if len(net_profile) != len(net_input):
            return jsonify({
                "error": f"Shape mismatch: net_profile ({len(net_profile)}), net_input ({len(net_input)})"
            }), 500

        net_cos_sim = cosine_similarity([net_profile], [net_input])[0][0]
        net_eu_dist = euclidean(net_profile, net_input)

        COS_THRESHOLD = 0.98
        EUC_THRESHOLD = 50
        NET_EUC_THRESHOLD = 400

        fused_score = (cosine_sim * 0.7) + (net_cos_sim * 0.3)

        if cosine_sim >= COS_THRESHOLD and net_cos_sim >= COS_THRESHOLD:
            is_genuine = True
        else:
            is_genuine = (
                fused_score >= 0.975 and
                eu_dist <= EUC_THRESHOLD and
                net_eu_dist <= NET_EUC_THRESHOLD
            )

        return jsonify({
            "prediction": "genuine" if is_genuine else "impostor",
            "cosine_similarity": round(cosine_sim, 4),
            "euclidean_distance": round(eu_dist, 2),
            "network_cosine": round(net_cos_sim, 4),
            "network_euclidean": round(net_eu_dist, 2),
            "fused_score": round(fused_score, 4)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server crashed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
