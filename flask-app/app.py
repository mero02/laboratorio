from flask import Flask, jsonify, request, render_template
import time

# Importa tracing
from instrumentation import setup_tracing
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Inicializa tracer
tracer = setup_tracing("flask-app")

app = Flask(__name__)

# Instrumenta Flask
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def index():
    with tracer.start_as_current_span("index-handler"):
        return render_template("index.html")

@app.route("/ping")
def ping():
    with tracer.start_as_current_span("ping-handler"):
        return jsonify({"status": "ok"}), 200

@app.route("/compute")
def compute():
    with tracer.start_as_current_span("compute-handler"):
        time.sleep(0.3)
        x = 5 * 5
        return jsonify({"operation": "5*5", "result": x}), 200

@app.route("/demo")
def demo():
    with tracer.start_as_current_span("demo-handler"):
        return render_template("demo.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
