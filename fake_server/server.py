from flask import Flask, request, jsonify
import ssl

app = Flask(__name__)

@app.route('/_/api/connect', methods=['POST'])
def connect():
    print(f"[+] License check request received")
    try:
        print(f"    Data: {request.get_json()}")
    except:
        pass
    return jsonify({
        "status": {
            "success": "True",
            "message": "OK"
        },
        "license": {
            "name": "Bypassed User",
            "expiration_date": "None",
            "current_machines": 1,
            "max_machines": 99,
            "product": "5218ed30-0b15-4a1c-8e64-0831e8081240"
        },
        "links": {
            "telegram": "",
            "signal": "",
            "main": "",
            "telegram_support": "",
            "signal_support": ""
        }
    })

@app.route('/_/api/log', methods=['POST'])
def log():
    print(f"[+] Log request received")
    return jsonify({"status": "ok"})

@app.route('/_/api/track', methods=['POST'])
def track():
    print(f"[+] Track request received")
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("=" * 60)
    print("[*] Fake LabelMaker License Server")
    print("=" * 60)
    print()
    print("[!] IMPORTANT: Add this line to C:\\Windows\\System32\\drivers\\etc\\hosts")
    print("    127.0.0.1 labelmaker.cc")
    print()
    print("[*] Starting HTTPS server on port 443...")
    print()
    
    # Run with self-signed cert
    app.run(host='0.0.0.0', port=443, ssl_context='adhoc', debug=False)
