import time
import subprocess
import pytesseract
from PIL import Image
import json
import os
import re
import logging
import pyautogui
from pywinauto import Application
import pygetwindow as gw

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define ADB command function
def adb_command(command):
    """Executes an ADB shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Error executing command: {command}\nError: {result.stderr}")
        return result.stdout.strip()
    except Exception as e:
        logging.exception(f"Exception occurred while executing command: {command}")
        return ""

# Function to take a screenshot
def take_screenshot(screenshot_path):
    """Captures a screenshot on the device and pulls it to the local machine."""
    adb_command("adb shell screencap -p /sdcard/screenshot.png")
    adb_command(f"adb pull /sdcard/screenshot.png {screenshot_path}")
    logging.info(f"Captured screenshot: {screenshot_path}")

# Function to close pop-up window
def close_popup():
    """Closes the pop-up window using ADB to send a back key event."""
    logging.info("Attempting to close pop-up using ADB back key event.")
    result = adb_command("adb shell input keyevent 4")  # Key event 4 is the back button
    logging.info(f"ADB command result: {result}")
    time.sleep(1)  # Add a delay to ensure the pop-up is closed

    # If the back key doesn't work, try tapping a specific coordinate
    if "error" in result.lower():
        logging.warning("Back key event failed, trying to tap coordinates.")
        adb_command("adb shell input tap 100 100")  # Example coordinates, adjust as needed
        time.sleep(1)

# Function to extract metadata and KXY from screenshot
def extract_metadata_from_screenshot(screenshot_path):
    """Extracts metadata and KXY data from a screenshot using OCR."""
    try:
        img = Image.open(screenshot_path)
        cropped_img = crop_bad_area(img)
        
        # Convert to grayscale to improve OCR accuracy
        gray_img = cropped_img.convert('L')
        
        text = pytesseract.image_to_string(gray_img)
        logging.info(f"OCR Output:\n{text}")
        
        kxy_data = None
        is_monster_tile = False
        for line in text.split("\n"):
            # Use regex to robustly extract KXY data
            match = re.search(r'K:\d+ X:\d+ Y:\d+', line)
            if match:
                kxy_data = match.group(0)
                break  # Stop after finding the first valid line
            if "Monster Hunt" in line or "DMG Boost" in line:
                is_monster_tile = True
        
        if kxy_data is None:
            logging.error("No KXY data found in OCR output. Stopping execution for debugging.")
            raise ValueError("No KXY data found in OCR output.")
        
        logging.info(f"Extracted KXY Data: {kxy_data}")
        logging.info(f"Is Monster Tile: {is_monster_tile}")
        return text, kxy_data, is_monster_tile
    except Exception as e:
        logging.exception("Error extracting metadata")
        return "", None, False

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
        logging.exception(f"Error loading tile coordinates from {filename}")
        return []

def click_point(x, y):
    """Clicks at the specified screen coordinates."""
    logging.info(f"Clicking at ({x}, {y})")
    pyautogui.moveTo(x, y, duration=0.5)
    pyautogui.click()

def type_text(text):
    """Types the specified text."""
    logging.info(f"Typing text: {text}")
    pyautogui.typewrite(text, interval=0.1)

def focus_target_window(window_title):
    """Focuses the target window based on the given title using pywinauto."""
    try:
        app = Application().connect(title=window_title)
        window = app.window(title=window_title)
        window.set_focus()
        time.sleep(2)  # Ensure the window is focused
        logging.info(f"Window '{window_title}' is active.")
    except Exception as e:
        logging.error(f"Error focusing on window: {e}")

def list_open_windows():
    """Logs all open window titles and returns them."""
    windows = gw.getAllTitles()
    logging.info("Open windows:")
    for i, title in enumerate(windows):
        logging.info(f"{i}: {title}")
    return windows

def select_window():
    """Prompts the user to select a window from the list."""
    windows = list_open_windows()
    if not windows:
        logging.error("No windows found.")
        return None
    try:
        choice = int(input("Enter the number of the window you want to focus on: "))
        if 0 <= choice < len(windows):
            return windows[choice]
        else:
            logging.error("Invalid choice.")
            return None
    except ValueError:
        logging.error("Invalid input. Please enter a number.")
        return None

# Main execution
def main():
    try:
        window_title = select_window()
        if window_title:
            focus_target_window(window_title)
        else:
            logging.error("No valid window selected. Exiting.")
            return
        
        logging.info("Starting script in 5 seconds. Please switch to the target window.")
        time.sleep(5)

        screenshot_folder = "screenshots"
        os.makedirs(screenshot_folder, exist_ok=True)

        log_file = "click_data.json"
        click_data = []

        if os.path.exists(log_file):
            try:
                with open(log_file, "r") as f:
                    click_data = json.load(f)
            except json.JSONDecodeError:
                logging.warning("Error decoding JSON, starting fresh.")

        tile_coordinates = load_tile_coordinates("tile_coordinates.json")

        for entry in tile_coordinates:
            x, y = entry['x'], entry['y']
            if is_point_in_bad_area(x, y):
                continue
            
            logging.info(f"Clicking point ({x}, {y})")
            click_point(x, y)
            time.sleep(1)  # Ensure the tap is registered

            screenshot_name = f"screenshot_x{x}_y{y}.png"
            screenshot_path = os.path.join(screenshot_folder, screenshot_name)
            take_screenshot(screenshot_path)
            
            if not os.path.exists(screenshot_path):
                logging.error(f"Screenshot {screenshot_path} not found.")
                continue
            
            try:
                metadata, kxy_data, is_monster_tile = extract_metadata_from_screenshot(screenshot_path)
            except ValueError as e:
                logging.error(f"Execution stopped: {e}")
                break
            
            logging.info(f"Detected monster tile: {is_monster_tile}")
            if not kxy_data or any(click['kxy'] == kxy_data for click in click_data):
                continue
            
            match = re.search(r'K:(\d+) X:(\d+) Y:(\d+)', kxy_data)
            if not match:
                logging.warning(f"Invalid KXY format '{kxy_data}'")
                continue
            
            click_entry = {"x": x, "y": y, "screenshot": screenshot_name, "metadata": metadata, "kxy": kxy_data}
            click_data.append(click_entry)
            
            close_popup()
            time.sleep(1)  # Ensure the pop-up is closed before proceeding
            
            try:
                with open(log_file, "w") as f:
                    json.dump(click_data, f, indent=4)
                logging.info(f"Data saved to {log_file}.")
            except Exception as e:
                logging.exception("Error writing to JSON file")
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
    finally:
        logging.info("Script terminated.")

if __name__ == "__main__":
    main()
