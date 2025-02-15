import subprocess
import os
import json
import time
from PIL import Image
import pytesseract

# Define ADB command function
def adb_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Function to take a screenshot
def take_screenshot(screenshot_name):
    adb_command(f"adb exec-out screencap -p > {screenshot_name}")
    print(f"Captured screenshot count: {len(click_data)}. {screenshot_name}")

# Function to crop the bad area from the image (for edge handling)
def crop_bad_area(image):
    bad_area = (396, 0, 1382, 82)
    cropped_image = image.copy()
    cropped_image.paste((255, 255, 255), (bad_area[0], bad_area[1], bad_area[2], bad_area[3]))
    return cropped_image

# Function to extract metadata and KXY from the screenshot (using OCR)
def extract_metadata_from_screenshot(screenshot_path):
    img = Image.open(screenshot_path)
    cropped_img = crop_bad_area(img)  # Crop out the bad area before running OCR
    text = pytesseract.image_to_string(cropped_img)
    kxy_data = None
    for line in text.split("\n"):
        if "K" in line and "X" in line and "Y" in line:
            kxy_data = line.strip()
    return text, kxy_data

# Initialize starting parameters for grid mapping
start_x = 16
start_y = 33
step_size = 60
num_steps_x = 53  # Example grid size (5x5)
num_steps_y = 27

screenshot_folder = "screenshots"
log_file = "click_data.json"
click_data = []

if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

# Check if JSON file exists, otherwise create it
if os.path.exists(log_file):
    with open(log_file, "r") as f:
        click_data = json.load(f)

# Main loop for grid mapping
for i in range(num_steps_x):
    for j in range(num_steps_y):
        x = start_x + i * step_size
        y = start_y + j * step_size
        print(f"Clicking point ({x}, {y})")
        adb_command(f"adb shell input tap {x} {y}")
        time.sleep(0.2)  # Allow for pop-up

        screenshot_name = f"{screenshot_folder}/screenshot_x{x}_y{y}.png"
        take_screenshot(screenshot_name)
        metadata, kxy_data = extract_metadata_from_screenshot(screenshot_name)

        click_entry = {
            "x": x,
            "y": y,
            "screenshot": screenshot_name,
            "metadata": metadata,
            "kxy": kxy_data if kxy_data else "Not Available"
        }
        click_data.append(click_entry)

        time.sleep(0.2)

# Save to JSON file after data collection
with open(log_file, "w") as f:
    json.dump(click_data, f, indent=4)

print(f"Data saved to {log_file}. count: {len(click_data)}")
