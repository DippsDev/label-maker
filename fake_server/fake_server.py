from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/_/api/connect', methods=['POST'])
def connect():
    print(f"[+] License check request received")
    print(f"    Data: {request.get_json()}")
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
    print("[*] Fake LabelMaker License Server")
    print("[*] Make sure to add '127.0.0.1 labelmaker.cc' to your hosts file")
    print("[*] Running on https://127.0.0.1:8443")
    print("[!] Note: App expects port 443. You may need to run as admin or use port forwarding.")
    print()
    app.run(host='0.0.0.0', port=8443, ssl_context='adhoc')
