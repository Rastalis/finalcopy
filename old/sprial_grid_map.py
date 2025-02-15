import time
import subprocess
import os
import pytesseract
from PIL import Image
import json
import math

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

# Spiral movement generator with boundary check (1600x900 screen)
def generate_spiral(start_x, start_y, max_radius, step_size, width=1600, height=900):
    # Generate spiral pattern while ensuring points are within the screen bounds
    points = []
    radius = 0
    angle = 0
    while radius <= max_radius:
        # Calculate next point in the spiral
        x = start_x + radius * math.cos(angle)
        y = start_y + radius * math.sin(angle)

        # Check if the point is within the screen bounds (1600x900)
        if 0 <= x < width and 0 <= y < height:
            points.append((int(x), int(y)))
        else:
            break  # Stop generating points if out of bounds

        angle += math.pi / 4  # Increase the angle to make a spiral
        radius += step_size  # Increase the radius to move outward
    return points

# Function to adjust grid mapping parameters based on new data
def adjust_grid_mapping(new_start_x, new_start_y, new_step_size, num_steps_x, num_steps_y):
    # Output the new grid mapping parameters
    print(f"Adjusted Starting Point: X={new_start_x}, Y={new_start_y}")
    print(f"Adjusted Step Size: {new_step_size}")
    print(f"Adjusted Number of Steps: X={num_steps_x}, Y={num_steps_y}")
    return new_start_x, new_start_y, new_step_size, num_steps_x, num_steps_y

# Main function to perform the grid scan and analyze
def main():
    # Define initial starting point and parameters
    start_x = 800
    start_y = 450
    max_radius = 800  # Maximum distance from the center
    step_size = 50    # Step size for each spiral turn
    num_steps_x = 32
    num_steps_y = 18

    # Generate spiral pattern, ensuring points stay within bounds
    points = generate_spiral(start_x, start_y, max_radius, step_size)
    
    # Folder to store screenshots
    screenshot_folder = "screenshots"
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)

    # JSON file to store the click data
    log_file = "click_data.json"
    click_data = []

    # Loop through the points and capture screenshots
    for point in points:
        x, y = point
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

    # Prompt for adjusting grid mapping based on analysis
    user_input = input("Would you like to try the suggested parameters for the next run? (yes/no): ")
    if user_input.lower() == 'yes':
        # Perform grid mapping adjustment based on analysis
        # In a real-world scenario, here you would use your analysis function to adjust parameters
        new_start_x, new_start_y, new_step_size, new_num_steps_x, new_num_steps_y = adjust_grid_mapping(start_x, start_y, step_size, num_steps_x, num_steps_y)
        # Proceed with the new grid mapping (adjusted params)
        print(f"Proceeding with new grid mapping: {new_start_x}, {new_start_y}, {new_step_size}")
    else:
        print("Scan completed. No further action taken.")

if __name__ == "__main__":
    main()
