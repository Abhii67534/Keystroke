from scapy.all import sniff
from datetime import datetime

def packet_callback(pkt):
    time = datetime.now().strftime('%H:%M:%S')
    src = pkt[0][1].src if hasattr(pkt[0][1], 'src') else "?"
    dst = pkt[0][1].dst if hasattr(pkt[0][1], 'dst') else "?"
    proto = pkt.summary().split()[0]
    size = len(pkt)

    print(f"[{time}] {proto:<8} | {src:<16} → {dst:<16} | {size} bytes")

print("🔍 Starting live packet sniff (10 seconds)...\n")

sniff(prn=packet_callback, timeout=15, store=0)

print("\n✅ Done sniffing.")
