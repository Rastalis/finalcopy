import time
import subprocess
import pytesseract
from PIL import Image
import json
import os
import re

# Define ADB command function
def adb_command(command):
    """Executes an ADB shell command and returns the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# Function to take a screenshot
def take_screenshot(screenshot_path):
    adb_command(f"adb exec-out screencap -p > {screenshot_path}")
    print(f"Captured screenshot: {screenshot_path}")

# Function to close pop-up window
def close_popup():
    adb_command("adb shell input keyevent 111")  # KEYCODE_ESCAPE
    print("Sent Escape key to close pop-up")

# Function to extract metadata and KXY from screenshot
def extract_metadata_from_screenshot(screenshot_path):
    """Extracts metadata and KXY data from a screenshot using OCR."""
    try:
        img = Image.open(screenshot_path)
        cropped_img = crop_bad_area(img)
        
        for section in [(0, 0, cropped_img.width, cropped_img.height // 3),
                        (0, cropped_img.height // 3, cropped_img.width, 2 * cropped_img.height // 3),
                        (0, 2 * cropped_img.height // 3, cropped_img.width, cropped_img.height)]:
            text = pytesseract.image_to_string(cropped_img.crop(section))
            for line in text.split("\n"):
                if "K" in line and "X" in line and "Y" in line:
                    print(f"Extracted KXY Data: {line.strip()}")
                    return text, line.strip()
        
        print("KXY data not found.")
        return text, None
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return "", None

# Crop bad areas
def crop_bad_area(image):
    """Crops out UI elements that interfere with OCR."""
    bad_area = (396, 0, 1382, 82)  # Adjust based on UI elements
    cropped_image = image.copy()
    cropped_image.paste((255, 255, 255), bad_area)
    return cropped_image

# Check if a point is within a bad area
def is_point_in_bad_area(x, y):
    """Returns True if the point is within a predefined bad area."""
    bad_areas = [
        ((396, 0), (1382, 82)),
        ((0, 589), (84, 765)),
        ((1468, 779), (1594, 894)),
        ((1522, 281), (1585, 335)),
    ]
    return any(x1 <= x <= x2 and y1 <= y <= y2 for (x1, y1), (x2, y2) in bad_areas)

# Load tile coordinates
def load_tile_coordinates(filename):
    """Loads tile coordinates from a JSON file."""
    try:
        with open(filename, "r") as f:
            return json.load(f).get("tiles", [])
    except Exception as e:
        print(f"Error loading tile coordinates: {e}")
        return []

# Main execution
screenshot_folder = "screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

screenshot_name = "center_tile_screenshot.png"
screenshot_path = os.path.join(screenshot_folder, screenshot_name)
take_screenshot(screenshot_path)
metadata, kxy_data = extract_metadata_from_screenshot(screenshot_path)

match = re.search(r'X:(\d+) Y:(\d+)', metadata)
center_tile_x, center_tile_y = match.groups() if match else ("Unknown", "Unknown")
log_file = f"click_data_x{center_tile_x}_y{center_tile_y}.json"

# Load previous click data
try:
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            click_data = json.load(f)
    else:
        click_data = []
except json.JSONDecodeError:
    print("Error decoding JSON, starting fresh.")
    click_data = []

# Process tile coordinates
tile_coordinates = load_tile_coordinates("tile_coordinates.json")
for entry in tile_coordinates:
    x, y = entry['x'], entry['y']
    if is_point_in_bad_area(x, y):
        continue
    
    print(f"Clicking point ({x}, {y})")
    adb_command(f"adb shell input tap {x} {y}")
    time.sleep(0.2)

    screenshot_name = f"screenshot_x{x}_y{y}.png"
    screenshot_path = os.path.join(screenshot_folder, screenshot_name)
    take_screenshot(screenshot_path)
    
    metadata, kxy_data = extract_metadata_from_screenshot(screenshot_path)
    if not kxy_data or any(click['kxy'] == kxy_data for click in click_data):
        continue
    
    click_entry = {"x": x, "y": y, "screenshot": screenshot_name, "metadata": metadata, "kxy": kxy_data}
    click_data.append(click_entry)
    
    close_popup()
    time.sleep(0.2)

# Save data to JSON
with open(log_file, "w") as f:
    json.dump(click_data, f, indent=4)
print(f"Data saved to {log_file}.")
