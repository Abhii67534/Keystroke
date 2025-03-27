# 🧠 Behavioral Biometric Authentication System

This project implements an **AI-powered behavioral biometrics system** that uses **keystroke dynamics** and **network behavior** to perform secure user authentication and behavioral drift analysis.

---

## 📌 Features

- ⌨️ **Keystroke Dynamics Authentication**  
  Detects user identity based on how they type — measuring timing features like hold time, latency, and flight time.

- 🌐 **Network Behavior Profiling**  
  Mocks user network activity per session (e.g., packet size, HTTP ratio), simulating device fingerprints.

- 🔄 **Time Series Drift Monitoring**  
  Visualizes behavior changes over time using charts (e.g., hold time trends, packet size trends).

- 📈 **Multi-metric Decision Logic**  
  Combines cosine similarity and Euclidean distance with weighted fusion for robust decision-making.

---

## 🧪 Demo Screenshots

### 📝 Enrollment & Verification
![Enrollment UI](screenshots/enroll.png)
![Verification Result](screenshots/verify.png)

### 📊 Behavioral Drift Charts
![Keystroke Drift](screenshots/keystroke-drift.png)
![Network Drift](screenshots/network-drift.png)

---

## ⚙️ Tech Stack

| Frontend (Next.js + React) | Backend (Flask + Python) | ML/Analytics |
|-----------------------------|--------------------------|--------------|
| Tailwind CSS               | Flask REST API           | Cosine Similarity |
| React Chart.js             | pandas, NumPy            | Euclidean Distance |
| Real-time keyboard capture | CORS-secured endpoints   | Time Series Charting |

---

## 🛠 How It Works

1. **User Enrolls** by typing a fixed phrase multiple times  
   ➜ System extracts behavioral features and stores them per user.

2. **Network Session** is mocked and stored (duration, packets, ratios).

3. **Verification** compares the new session against the stored profiles using:
   - `cosine_similarity`
   - `euclidean_distance`
   - Weighted fusion of keystroke & network biometrics

4. **Access Decision**: If similarity and distance pass thresholds → 🟢 Access Granted

5. **Charts Update** after every session — showing how your typing and network drift over time.

---

## 🚀 Getting Started

### 1. Backend (Python + Flask)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
