```python
from flask import Flask, request, jsonify
import subprocess
import os
import json
import tempfile

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

QIMEN_QIJU = os.path.join(
    BASE_DIR,
    "tools",
    "bin",
    "qimen_qiju.sh"
)


@app.route("/")
def home():
    return jsonify({
        "service": "qmenpowers-api",
        "status": "ok"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/api/qimen/qiju", methods=["POST"])
def qimen_qiju():

    data = request.get_json(silent=True) or {}

    datetime_value = data.get("datetime")
    plate_type = data.get("type", "event")
    tianqin = data.get("tianqin", "follow-tiannei")

    if not datetime_value:
        return jsonify({
            "success": False,
            "error": "datetime is required"
        }), 400

    if plate_type not in ("event", "birth"):
        return jsonify({
            "success": False,
            "error": "type must be event or birth"
        }), 400

    allowed_tianqin = (
        "follow-tiannei",
        "jikun",
        "follow-zhifu"
    )

    if tianqin not in allowed_tianqin:
        return jsonify({
            "success": False,
            "error": "invalid tianqin mode"
        }), 400

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".json",
            delete=False
        ) as tmp:

            output_path = tmp.name

        command = [
            QIMEN_QIJU,
            f"--type={plate_type}",
            f"--tianqin={tianqin}",
            f"--output={output_path}",
            datetime_value
        ]

        result = subprocess.run(
            command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:

            return jsonify({
                "success": False,
                "error": "Qi Men calculation failed",
                "returncode": result.returncode,
                "stderr": result.stderr,
                "stdout": result.stdout
            }), 500

        try:

            with open(
                output_path,
                "r",
                encoding="utf-8"
            ) as f:

                calculation = json.load(f)

        except Exception as e:

            return jsonify({
                "success": False,
                "error": "Unable to read calculation JSON",
                "details": str(e),
                "stdout": result.stdout,
                "stderr": result.stderr
            }), 500

        finally:

            try:
                os.unlink(output_path)
            except OSError:
                pass

        return jsonify({
            "success": True,
            "type": plate_type,
            "datetime": datetime_value,
            "tianqin": tianqin,
            "calculation": calculation
        })

    except subprocess.TimeoutExpired:

        return jsonify({
            "success": False,
            "error": "Calculation timed out"
        }), 504

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
```

