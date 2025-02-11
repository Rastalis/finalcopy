import time
import subprocess
import os
import pytesseract
from PIL import Image
import json

# Define ADB command function
def adb_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Function to take screenshot
def take_screenshot(screenshot_name):
    adb_command(f"adb exec-out screencap -p > {screenshot_name}")
    print(f"Captured screenshot: {screenshot_name}")

# Function to close the pop-up window by sending the Escape key (keycode 111)
def close_popup():
    # Send the Escape key (keycode 111) to close the pop-up
    adb_command("adb shell input keyevent 111")  # 111 corresponds to KEYCODE_ESCAPE
    print("Sent Escape key to close pop-up")

# Function to extract metadata and KXY from the screenshot (using OCR)
def extract_metadata_from_screenshot(screenshot_path):
    img = Image.open(screenshot_path)
    # Crop the image to exclude the bad area before running OCR
    cropped_img = crop_bad_area(img)
    text = pytesseract.image_to_string(cropped_img)

    # Debug: Print OCR output to see what was extracted
    print(f"OCR Output:\n{text}")

    # Extract KXY from the OCR text (assuming KXY format is consistent)
    kxy_data = None
    for line in text.split("\n"):
        if "K" in line and "X" in line and "Y" in line:
            kxy_data = line.strip()

    print(f"Extracted KXY Data: {kxy_data}")
    
    return text, kxy_data

# Function to crop the bad area from the image
def crop_bad_area(image):
    # Define bad area coordinates (x1, y1, x2, y2)
    bad_area = (396, 0, 1382, 82)
    cropped_image = image.copy()
    # Crop out the bad area (this will cut the bad area from the image)
    cropped_image.paste((255, 255, 255), (bad_area[0], bad_area[1], bad_area[2], bad_area[3]))
    return cropped_image

# Function to check if the point is inside any of the bad areas
def is_point_in_bad_area(x, y):
    # Define bad areas
    bad_areas = [
        ((396, 0), (1382, 82)),
        ((0, 589), (84, 765)),
        ((1468, 779), (1594, 894)),
        ((1522, 281), (1585, 335)),
    ]
    
    # Check if the point is within any of the bad areas
    for area in bad_areas:
        (x1, y1), (x2, y2) = area
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
    return False

# Function to shrink the list of ADB points to the minimum number to cover all tiles
def reduce_to_minimum_points(click_data, step_size):
    # Placeholder: Assuming we want to reduce to minimal unique KXY points
    unique_points = set((entry['kxy'] for entry in click_data if entry['kxy'] != 'Not Available'))
    print(f"Unique KXY Tiles: {len(unique_points)}")
    
    # For now, we just return the unique points, could implement further logic to decide minimal points
    reduced_click_data = [entry for entry in click_data if entry['kxy'] in unique_points]
    print(f"Reduced points to {len(reduced_click_data)}")
    
    return reduced_click_data

# Set starting point
start_x = 16  # Starting X coordinate
start_y = 33  # Starting Y coordinate
step_size = 30  # Small step size to cover more ground

# Number of steps (You can modify this based on the grid size)
num_steps_x = 53  # Number of steps along the X axis
num_steps_y = 27  # Number of steps along the Y axis

# Folder to store screenshots
screenshot_folder = "screenshots"
if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

# JSON file to store the click data
log_file = "click_data.json"
click_data = []

# Loop through the grid, clicking each point and capturing metadata
for i in range(num_steps_x):
    for j in range(num_steps_y):
        # Calculate the ADB point
        x = start_x + i * step_size
        y = start_y + j * step_size

        # Skip click if the point is inside any bad area
        if is_point_in_bad_area(x, y):
            print(f"Skipping point ({x}, {y}) - Inside bad area.")
            continue

        # Click on ADB point
        print(f"Clicking point ({x}, {y})")
        adb_command(f"adb shell input tap {x} {y}")
        time.sleep(0.2)  # Give time for the pop-up to appear

        # Take a screenshot and save it with the naming convention
        screenshot_name = f"{screenshot_folder}/screenshot_x{x}_y{y}.png"
        take_screenshot(screenshot_name)

        # Extract metadata and KXY from the screenshot (pop-up window OCR)
        metadata, kxy_data = extract_metadata_from_screenshot(screenshot_name)

        # Store the collected data in the log
        click_entry = {
            "x": x,
            "y": y,
            "screenshot": screenshot_name,
            "metadata": metadata,
            "kxy": kxy_data if kxy_data else "Not Available"  # Handle None KXY
        }
        
        # Append to the JSON log
        click_data.append(click_entry)

        # Close the pop-up by sending the Escape key
        close_popup()

        # Sleep before next action
        time.sleep(0.2)

# Save the log data to a JSON file
try:
    with open(log_file, "w") as f:
        json.dump(click_data, f, indent=4)
    print(f"Data saved to {log_file}.")
except Exception as e:
    print(f"Error saving to JSON file: {e}")

# Once the scan is complete, reduce the list to the minimum number of points
click_data = reduce_to_minimum_points(click_data, step_size)

# Save the reduced data to a new JSON file for further processing
reduced_log_file = "reduced_click_data.json"
try:
    with open(reduced_log_file, "w") as f:
        json.dump(click_data, f, indent=4)
    print(f"Reduced data saved to {reduced_log_file}.")
except Exception as e:
    print(f"Error saving reduced data to JSON file: {e}")
