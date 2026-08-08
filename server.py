from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "service": "qmenpowers-api"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/qimen", methods=["POST"])
def qimen():
    data = request.get_json(silent=True) or {}

    datetime_value = data.get("datetime")

    if not datetime_value:
        return jsonify({
            "error": "datetime is required"
        }), 400

    script = os.path.join(
        BASE_DIR,
        "tools",
        "bin",
        "qimen_qiju.sh"
    )

    try:
        result = subprocess.run(
            [script, datetime_value],
            capture_output=True,
            text=True,
            timeout=30
        )

        return jsonify({
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "error": "Calculation timed out"
        }), 504

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
