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
    print("📂 Loading templates...")  # Debugging
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as f:
            try:
                data = json.load(f)
                print(f"✅ Loaded templates: {data}")  # Debugging
                return data
            except json.JSONDecodeError as e:
                print(f"❌ JSON Load Error: {e}")  # Debugging
                return {}  # Return empty if file is corrupted
    return {}


# Save templates
def save_templates(templates):
    print(f"💾 Saving templates: {templates}")  # Debugging
    try:
        with open(TEMPLATE_FILE, "w") as f:
            json.dump(templates, f, indent=4)
        print("✅ Successfully saved templates!")  # Debugging
    except Exception as e:
        print(f"❌ Error writing JSON: {e}")  # Debugging


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
        data = request.get_json(silent=True)
        print(f"📥 Parsed JSON: {data}")

        if not data:
            return jsonify({"error": "No data received or invalid JSON"}), 400

        template_name = data.get("name")
        if not template_name:
            return jsonify({"error": "Template name required"}), 400

        x1, y1, x2, y2 = data["x1"], data["y1"], data["x2"], data["y2"]

        # 🚨 Check if screenshot exists before processing
        if not os.path.exists(LOCAL_SCREENSHOT_PATH):
            print("❌ Screenshot file missing!")
            return jsonify({"error": "Screenshot not found"}), 404

        # Load screenshot
        img = cv2.imread(LOCAL_SCREENSHOT_PATH)
        if img is None:
            print("❌ Failed to read screenshot!")
            return jsonify({"error": "Screenshot could not be read"}), 500

        # 🚨 Check if ROI coordinates are within bounds
        h, w, _ = img.shape
        if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
            print("❌ ROI coordinates out of bounds!")
            return jsonify({"error": "ROI coordinates out of bounds"}), 400

        # Crop and save ROI
        roi = img[y1:y2, x1:x2]
        template_path = os.path.join(TEMPLATE_FOLDER, f"{template_name}.png")

        if not cv2.imwrite(template_path, roi):
            print("❌ Failed to save template image!")
            return jsonify({"error": "Failed to save template image"}), 500

        # Save template metadata
        templates = load_templates()
        templates[template_name] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "path": template_path}
        save_templates(templates)

        print("✅ Template saved successfully!")
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
            return jsonify({"found": False, "message": "Template not found"}), 404

        template_info = templates[template_name]
        template_path = template_info["path"]

        img = cv2.imread(LOCAL_SCREENSHOT_PATH, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

        if img is None or template is None:
            return jsonify({"error": "Screenshot or template missing"}), 404

        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        locations = np.where(result >= threshold)

        matches = []
        h, w = template.shape

        for pt in zip(*locations[::-1]):
            matches.append({
                "x1": int(pt[0]),  # ✅ Convert NumPy int64 to Python int
                "y1": int(pt[1]),
                "x2": int(pt[0] + w),
                "y2": int(pt[1] + h)
            })

        return jsonify({"found": len(matches) > 0, "matches": matches})

    except Exception as e:
        print(f"❌ Error in search_template: {str(e)}")  # Debugging output
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
