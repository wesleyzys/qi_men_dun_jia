from flask import Flask, request, jsonify, render_template
import subprocess
import json
import os

app = Flask(__name__, template_folder=".")

BIN_DIR = "./tools/bin"

def run_bash_script(cmd):
    """Executes a CLI command and returns the output JSON."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/qiju', methods=['POST'])
def qiju():
    data = request.json
    dt = data.get('datetime')
    plate_type = data.get('type', 'birth')
    
    cmd = f"{BIN_DIR}/qimen_qiju.sh --type={plate_type} \"{dt}\""
    run_bash_script(cmd)
    
    file_path = "./qmen_birth.json" if plate_type == "birth" else "./qmen_event.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Failed to generate plate"}), 500

@app.route('/api/caiguan', methods=['POST'])
def caiguan():
    run_bash_script(f"{BIN_DIR}/qimen_caiguan.sh")
    if os.path.exists("./qmen_caiguan.json"):
        with open("./qmen_caiguan.json", "r") as f:
            return jsonify(json.load(f))
    return jsonify({"message": "Caiguan processing complete"})

@app.route('/api/huaqizhen', methods=['POST'])
def huaqizhen():
    run_bash_script(f"{BIN_DIR}/qimen_huaqizhen.sh")
    if os.path.exists("./qmen_huaqizhen.json"):
        with open("./qmen_huaqizhen.json", "r") as f:
            return jsonify(json.load(f))
    return jsonify({"message": "Huaqizhen processing complete"})

@app.route('/api/yishenhuanjiang', methods=['POST'])
def yishenhuanjiang():
    run_bash_script(f"{BIN_DIR}/qimen_yishenhuanjiang.sh")
    if os.path.exists("./qmen_yishenhuanjiang.json"):
        with open("./qmen_yishenhuanjiang.json", "r") as f:
            return jsonify(json.load(f))
    return jsonify({"message": "Transformation complete"})

@app.route('/api/hunlian', methods=['POST'])
def hunlian():
    run_bash_script(f"{BIN_DIR}/qimen_hunlian.sh")
    if os.path.exists("./qmen_hunlian.json"):
        with open("./qmen_hunlian.json", "r") as f:
            return jsonify(json.load(f))
    return jsonify({"message": "Hunlian complete"})

@app.route('/api/xingge', methods=['POST'])
def xingge():
    run_bash_script(f"{BIN_DIR}/qimen_xingge.sh")
    if os.path.exists("./qmen_xingge.json"):
        with open("./qmen_xingge.json", "r") as f:
            return jsonify(json.load(f))
    return jsonify({"message": "Personality analysis complete"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
