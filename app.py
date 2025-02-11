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

# Capture Screenshot from ADB
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
        print("🔍 Checking incoming request...")
        print(f"Headers: {request.headers}")  # Log headers
        print(f"Raw Data: {request.data}")    # Log raw request data
        data = request.get_json(silent=True)  # Prevent exception if JSON is invalid
        print(f"Parsed JSON: {data}")         # Log parsed JSON

        if not data:
            return jsonify({"error": "No data received or invalid JSON"}), 400

        template_name = data.get("name")
        if not template_name:
            return jsonify({"error": "Template name required"}), 400

        x1, y1, x2, y2 = data["x1"], data["y1"], data["x2"], data["y2"]

        # Load screenshot
        img = cv2.imread(LOCAL_SCREENSHOT_PATH)
        if img is None:
            return jsonify({"error": "Screenshot not found"}), 404

        # Save metadata
        templates = load_templates()
        templates[template_name] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        save_templates(templates)

        return jsonify({"status": "Template saved", "name": template_name})

    except Exception as e:
        print(f"❌ Error saving template: {str(e)}")  # Debugging output
        return jsonify({"error": f"Save failed: {str(e)}"}), 500



# Search for template in screenshot using Image Matching
@app.route("/search_template", methods=["POST"])
def search_template():
    try:
        data = request.json
        template_name = data.get("name")
        templates = load_templates()

        if template_name not in templates:
            print(f"❌ Template '{template_name}' not found in database.")
            return jsonify({"found": False, "message": "Template not found"}), 404

        template_info = templates[template_name]
        template_path = template_info["path"]

        # Load images
        if not os.path.exists(LOCAL_SCREENSHOT_PATH):
            print("❌ Screenshot file not found.")
            return jsonify({"error": "Screenshot not found"}), 404

        if not os.path.exists(template_path):
            print(f"❌ Template image file '{template_name}.png' not found.")
            return jsonify({"error": "Template image not found"}), 404

        img = cv2.imread(LOCAL_SCREENSHOT_PATH, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            print("❌ Failed to load screenshot image.")
            return jsonify({"error": "Screenshot failed to load"}), 500
        if template is None:
            print(f"❌ Failed to load template '{template_name}.png'")
            return jsonify({"error": "Template image failed to load"}), 500

        # Apply template matching
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        locations = np.where(result >= threshold)

        matches = []
        h, w = template.shape

        for pt in zip(*locations[::-1]):
            matches.append({"x1": pt[0], "y1": pt[1], "x2": pt[0] + w, "y2": pt[1] + h})

        print(f"✅ Found {len(matches)} matches for template '{template_name}'")
        return jsonify({"found": len(matches) > 0, "matches": matches})

    except Exception as e:
        print(f"❌ Error in search_template: {str(e)}")
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
        return jsonify({"error": "Failed to send tap"}), 500

# Main Page
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
