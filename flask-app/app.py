from flask import Flask, jsonify, request
import time

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "Microservicio Flask funcionando"}), 200

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"}), 200

@app.route("/compute")
def compute():
    # Simulamos una operación
    time.sleep(0.3)
    x = 5 * 5
    return jsonify({"operation": "5*5", "result": x}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
