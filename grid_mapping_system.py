import time
import subprocess
import pytesseract
from PIL import Image
import json
import numpy as np
import os
import re

# Define ADB command function
def adb_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Function to take screenshot
def take_screenshot(screenshot_name, screenshot_folder):
    adb_command(f"adb exec-out screencap -p > {screenshot_folder}/{screenshot_name}")
    print(f"Captured screenshot: {screenshot_folder}/{screenshot_name}")

# Function to close the pop-up window by sending the Escape key (keycode 111)
def close_popup():
    adb_command("adb shell input keyevent 111")  # 111 corresponds to KEYCODE_ESCAPE
    print("Sent Escape key to close pop-up")

# Function to extract metadata and KXY from the screenshot (using OCR)
def extract_metadata_from_screenshot(screenshot_path):
    img = Image.open(screenshot_path)
    cropped_img = crop_bad_area(img)  # Crop bad area to improve OCR accuracy
    text = pytesseract.image_to_string(cropped_img)  # Use the entire screenshot for OCR
    print(f"OCR Output:\n{text}")
    kxy_data = None
    for line in text.split("\n"):
        if "K" in line and "X" in line and "Y" in line:
            kxy_data = line.strip()
    if kxy_data is None:
        cropped_img_top = cropped_img.crop((0, 0, cropped_img.width, cropped_img.height // 3))
        text_top = pytesseract.image_to_string(cropped_img_top)
        for line in text_top.split("\n"):
            if "K" in line and "X" in line and "Y" in line:
                kxy_data = line.strip()
    if kxy_data is None:
        cropped_img_middle = cropped_img.crop((0, cropped_img.height // 3, cropped_img.width, 2 * cropped_img.height // 3))
        text_middle = pytesseract.image_to_string(cropped_img_middle)
        for line in text_middle.split("\n"):
            if "K" in line and "X" in line and "Y" in line:
                kxy_data = line.strip()
    if kxy_data is None:
        cropped_img_bottom = cropped_img.crop((0, 2 * cropped_img.height // 3, cropped_img.width, cropped_img.height))
        text_bottom = pytesseract.image_to_string(cropped_img_bottom)
        for line in text_bottom.split("\n"):
            if "K" in line and "X" in line and "Y" in line:
                kxy_data = line.strip()
    print(f"Extracted KXY Data: {kxy_data}")
    return text, kxy_data

# Crop bad areas (adjust coordinates for edge detection)
def crop_bad_area(image):
    bad_area = (396, 0, 1382, 82)  # Example, change based on edge areas
    cropped_image = image.copy()
    cropped_image.paste((255, 255, 255), (bad_area[0], bad_area[1], bad_area[2], bad_area[3]))
    return cropped_image

# Check if point is within bad area
def is_point_in_bad_area(x, y, is_ocr=True):
    bad_areas = [
        ((396, 0), (1382, 82)),
        ((0, 589), (84, 765)),
        ((1468, 779), (1594, 894)),
        ((1522, 281), (1585, 335)),
    ]
    for area in bad_areas:
        (x1, y1), (x2, y2) = area
        if x1 <= x <= x2 and y1 <= y <= y2:
            return is_ocr
    return False

# Crop the pop-up window (used for template extraction)
def crop_popup_window(image):
    # Define the coordinates for the region of the pop-up window you want to capture
    left = 596  # X coordinate of the left edge of the pop-up
    top = 156   # Y coordinate of the top edge of the pop-up
    right = 788  # X coordinate of the right edge of the pop-up
    bottom = 247  # Y coordinate of the bottom edge of the pop-up

    # Crop the image to the defined region
    cropped_image = image.crop((left, top, right, bottom))

    return cropped_image

# Set up grid mapping and step size
# start_x, start_y = 16, 33
# step_size = 50
# num_steps_x, num_steps_y = 32, 18

# Take a screenshot and read the text from the specified ROI
screenshot_name = "center_tile_screenshot.png"
screenshot_folder = "screenshots"
take_screenshot(screenshot_name, screenshot_folder)
metadata, kxy_data = extract_metadata_from_screenshot(f"{screenshot_folder}/{screenshot_name}")

# Extract the X and Y coordinates from the text
match = re.search(r'X:(\d+) Y:(\d+)', metadata)
if match:
    center_tile_x, center_tile_y = match.groups()
else:
    print("No match found")
    # Handle this case appropriately

# Clean the extracted text
cleaned_metadata = re.sub(r'\W+', ' ', metadata)

# Use the extracted coordinates to name the JSON file
log_file = f"click_data_x{center_tile_x}_y{center_tile_y}.json"

# Screenshot folder and log file setup
if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)
if not os.path.exists(log_file):
    click_data = []
else:
    with open(log_file, "r") as f:
        click_data = json.load(f)

# Load the tile coordinates
with open('tile_coordinates.json', 'r') as f:
    tile_coordinates = json.load(f)

# Loop through the tile coordinates, clicking and taking screenshots
for entry in tile_coordinates['tiles']:
    x, y = entry['x'], entry['y']

    if is_point_in_bad_area(x, y, is_ocr=False):
        continue

    print(f"Clicking point ({x}, {y})")
    adb_command(f"adb shell input tap {x} {y}")
    time.sleep(0.2)

    screenshot_name = f"{screenshot_folder}/screenshot_x{x}_y{y}.png"
    take_screenshot(screenshot_name, screenshot_folder)
    
    metadata, kxy_data = extract_metadata_from_screenshot(f"{screenshot_folder}/{screenshot_name}")
    
    if kxy_data is None:
        print(f"KXY data not found for point ({x}, {y})")
        continue

    if kxy_data in [click['kxy'] for click in click_data]:
        continue

    click_entry = {
        "x": x, "y": y, "screenshot": screenshot_name,
        "metadata": metadata, "kxy": kxy_data if kxy_data else "Not Available"
    }
    click_data.append(click_entry)

    close_popup()
    time.sleep(0.2)

    # Save data to JSON
    with open(log_file, "a") as f:
        json.dump(click_entry, f, indent=4)
    print(f"Data saved to {log_file}.")

# Save data to JSON
with open(log_file, "w") as f:
    json.dump(click_data, f, indent=4)
print(f"Data saved to {log_file}.") 