from flask import Flask, render_template, request, jsonify
import subprocess
import os
import json
import cv2
import numpy as np

app = Flask(__name__)

ADB_SCREENSHOT_PATH = "/sdcard/screenshot.png"
LOCAL_SCREENSHOT_PATH = "static/screenshot.png"
TEMPLATE_FOLDER = "static/templates"
TEMPLATE_FILE = "templates.json"

# Ensure template folder exists
os.makedirs(TEMPLATE_FOLDER, exist_ok=True)

# Load templates
def load_templates():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as f:
            return json.load(f)
    return {}

# Save templates
def save_templates(templates):
    with open(TEMPLATE_FILE, "w") as f:
        json.dump(templates, f, indent=4)

# Capture Screenshot
@app.route("/capture")
def capture_screenshot():
    try:
        device_connected = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        if "device" not in device_connected.stdout:
            return jsonify({"error": "No ADB device found"}), 400

        # Remove old screenshot to ensure a fresh pull
        if os.path.exists(LOCAL_SCREENSHOT_PATH):
            os.remove(LOCAL_SCREENSHOT_PATH)

        subprocess.run(["adb", "shell", "screencap", "-p", ADB_SCREENSHOT_PATH])
        subprocess.run(["adb", "pull", ADB_SCREENSHOT_PATH, LOCAL_SCREENSHOT_PATH])

        # Ensure the file was pulled successfully
        if not os.path.exists(LOCAL_SCREENSHOT_PATH):
            return jsonify({"error": "Screenshot capture failed"}), 500

        print("✅ Screenshot updated successfully")  # Debugging
        return jsonify({"status": "success"})

    except Exception as e:
        print(f"❌ Screenshot capture error: {str(e)}")  # Debugging
        return jsonify({"error": f"Capture failed: {str(e)}"}), 500

# Save ROI as a template (stores image + metadata)
@app.route("/save_template", methods=["POST"])
def save_template():
    try:
        # ✅ Check if the request contains JSON
        if not request.is_json:
            print("❌ Error: Received non-JSON request")  # Debugging
            return jsonify({"error": "Invalid request, expected JSON"}), 400

        data = request.get_json()

        # ✅ Ensure required fields exist
        if not data or "name" not in data or "x1" not in data:
            print(f"❌ Error: Missing required data {data}")  # Debugging
            return jsonify({"error": "Missing required template data"}), 400

        template_name = data["name"].strip()
        x1, y1, x2, y2 = data["x1"], data["y1"], data["x2"], data["y2"]

        if not template_name:
            return jsonify({"error": "Template name cannot be empty"}), 400

        # ✅ Check if screenshot exists
        if not os.path.exists(LOCAL_SCREENSHOT_PATH):
            return jsonify({"error": "Screenshot not found"}), 404

        # ✅ Load screenshot and save ROI
        img = cv2.imread(LOCAL_SCREENSHOT_PATH)
        if img is None:
            return jsonify({"error": "Failed to load screenshot"}), 500

        roi = img[y1:y2, x1:x2]
        template_path = os.path.join(TEMPLATE_FOLDER, f"{template_name}.png")
        cv2.imwrite(template_path, roi)

        # ✅ Save metadata
        templates = load_templates()
        templates[template_name] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "path": template_path}
        save_templates(templates)

        print(f"✅ Template '{template_name}' saved successfully")
        return jsonify({"status": "Template saved", "name": template_name})

    except Exception as e:
        print(f"❌ Save template error: {str(e)}")
        return jsonify({"error": f"Save failed: {str(e)}"}), 500


@app.route("/search_template", methods=["POST"])
def search_template():
    try:
        if not request.is_json:
            print("❌ Error: Received non-JSON request")  # Debugging
            return jsonify({"error": "Invalid request, expected JSON"}), 400

        data = request.get_json()
        if not data or "name" not in data:
            print(f"❌ Error: Missing template name {data}")  # Debugging
            return jsonify({"error": "Missing template name"}), 400

        template_name = data["name"].strip()
        templates = load_templates()

        if template_name not in templates:
            print(f"❌ Template '{template_name}' not found")  # Debugging
            return jsonify({"found": False, "message": "Template not found"}), 404

        return jsonify({"found": True, "roi": templates[template_name]})

    except Exception as e:
        print(f"❌ Search template error: {str(e)}")
        return jsonify({"error": f"Search failed: {str(e)}"}), 500


# Handle Live Clicks (Send tap to ADB)
@app.route("/live_click", methods=["POST"])
def live_click():
    try:
        data = request.json
        x, y = int(data["x"]), int(data["y"])

        print(f"✅ Live Click at ({x}, {y}) sent to ADB")  # Debugging log
        subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])

        return jsonify({"status": "tap_sent", "x": x, "y": y})

    except Exception as e:
        print(f"❌ Live Click error: {str(e)}")  # Debugging
        return jsonify({"error": "Failed to send tap"}), 500

# Main Page
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
