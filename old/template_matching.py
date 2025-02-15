import cv2
import numpy as np
import os
import time
from PIL import Image
import pytesseract
import subprocess
import json

def close_popup():
    adb_command("adb shell input keyevent 111")  # 111 corresponds to KEYCODE_ESCAPE
    print("Sent Escape key to close pop-up")
    
    # ADB command to interact with the device
def adb_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Function to take screenshot
def take_screenshot(screenshot_name):
    adb_command(f"adb exec-out screencap -p > {screenshot_name}")
    print(f"Captured screenshot: {screenshot_name}")

# Function to crop the image to remove bad areas
def crop_bad_area(image):
    bad_area = (396, 0, 1382, 82)  # Example of bad area, adjust for screen size
    cropped_image = image.copy()
    cropped_image.paste((255, 255, 255), (bad_area[0], bad_area[1], bad_area[2], bad_area[3]))
    return cropped_image

# Function to extract metadata and KXY using OCR
def extract_metadata_from_screenshot(screenshot_path):
    img = Image.open(screenshot_path)
    cropped_img = crop_bad_area(img)  # Crop the image to improve OCR accuracy
    text = pytesseract.image_to_string(cropped_img)
    print(f"OCR Output:\n{text}")
    
    kxy_data = None
    for line in text.split("\n"):
        if "K" in line and "X" in line and "Y" in line:
            kxy_data = line.strip()
    print(f"Extracted KXY Data: {kxy_data}")
    return text, kxy_data

# Load templates for different tile types (castles, darknests, etc.)
def load_templates(template_folder="templates"):
    templates = {}
    for template_file in os.listdir(template_folder):
        if template_file.endswith(".png"):
            template_path = os.path.join(template_folder, template_file)
            template_name = template_file.split('.')[0]  # Use filename without extension as name
            templates[template_name] = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    return templates

# Perform template matching on the screenshot
def match_template(image, template, thresholds=[0.8, 0.9]):
    matched_locations = []
    for threshold in thresholds:
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        matched_locations.append(locations)
    return matched_locations

# Adjust the template size based on the zoom level (scale)
def adjust_template_size(template, zoom_factor):
    new_width = int(template.shape[1] * zoom_factor)
    new_height = int(template.shape[0] * zoom_factor)
    return cv2.resize(template, (new_width, new_height))

# Adjust grid size based on density of KXY data
def adjust_grid_based_on_density(kxy_data, current_step_size):
    density = len(kxy_data) / current_step_size
    if density > 0.5:
        current_step_size -= 10  # Decrease step size in dense areas
    else:
        current_step_size += 10  # Increase step size in sparse areas
    return current_step_size

def detect_partial_tiles(image, template):
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= 0.8)
    # Logic to check if the template is partially visible
    # If so, capture the coordinates and size of the partial match
    return locations

# Function to capture template from pop-up window (if applicable)
def capture_template_from_popup(x, y):
    screenshot_name = f"templates/template_x{x}_y{y}.png"
    
    adb_command(f"adb shell screencap -p /sdcard/screenshot.png")  # Capture full screen
    adb_command(f"adb pull /sdcard/screenshot.png {screenshot_name}")  # Pull the screenshot

    # Crop the pop-up window from the full screenshot
    img = cv2.imread(screenshot_name, cv2.IMREAD_GRAYSCALE)
    template = crop_popup_window(img)  # Crop the pop-up window to the defined region
    cv2.imwrite(f"templates/template_x{x}_y{y}.png", template)

    print(f"Captured template for tile at ({x}, {y})")

# Crop the pop-up window (define region based on screen size and pop-up location)
def crop_popup_window(image):
    left = 100  # X coordinate of the left edge of the pop-up
    top = 100   # Y coordinate of the top edge of the pop-up
    right = 500 # X coordinate of the right edge of the pop-up
    bottom = 500 # Y coordinate of the bottom edge of the pop-up

    cropped_image = image[top:bottom, left:right]
    return cropped_image

# Main function for setting up grid mapping and template matching
def main():
    start_x, start_y = 16, 33
    step_size = 50
    num_steps_x, num_steps_y = 32, 18

    screenshot_folder = "screenshots"
    log_file = "click_data.json"

    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)

    if not os.path.exists(log_file):
        click_data = []
    else:
        with open(log_file, "r") as f:
            click_data = json.load(f)

    templates = load_templates()  # Load all templates for tiles

    # Loop through grid and match templates
    for i in range(num_steps_x):
        for j in range(num_steps_y):
            x = start_x + i * step_size
            y = start_y + j * step_size

            print(f"Clicking point ({x}, {y})")
            adb_command(f"adb shell input tap {x} {y}")
            time.sleep(0.2)

            screenshot_name = f"{screenshot_folder}/screenshot_x{x}_y{y}.png"
            take_screenshot(screenshot_name)

            metadata, kxy_data = extract_metadata_from_screenshot(screenshot_name)

            # Open the screenshot for template matching
            img = cv2.imread(screenshot_name, cv2.IMREAD_GRAYSCALE)

            # Try matching all templates to the screenshot
            for template_name, template in templates.items():
                print(f"Matching template for {template_name}")
                locations = match_template(img, template)
                
                if len(locations[0]) > 0:  # If matching locations are found
                    print(f"Match found for {template_name} at ({x}, {y})")
                    # You can store or process matches here, like adding them to a database
                    click_entry = {
                        "x": x, "y": y, "template": template_name,
                        "screenshot": screenshot_name, "kxy": kxy_data
                    }
                    click_data.append(click_entry)

            close_popup()
            time.sleep(0.2)

    # Save data to JSON
    with open(log_file, "w") as f:
        json.dump(click_data, f, indent=4)
    print(f"Data saved to {log_file}.")

if __name__ == "__main__":
    main()
