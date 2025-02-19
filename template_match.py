import os
import cv2
import numpy as np
import subprocess
import time
from datetime import datetime

# Ensure directories exist
os.makedirs('screenshots', exist_ok=True)

# Paths
TEMPLATES_DIR = "game_templates"
SCREENSHOT_PATH = "screenshots/latest_screenshot.png"

def check_adb_connection():
    """Check if an ADB device is connected before starting."""
    try:
        output = subprocess.check_output(['adb', 'devices']).decode()
        if "device" not in output.split("\n")[1]:
            print("No ADB device found. Please connect a device.")
            exit(1)
    except Exception as e:
        print(f"ADB check failed: {e}")
        exit(1)

def take_screenshot():
    """Takes a new screenshot and saves it."""
    try:
        subprocess.run(['adb', 'shell', 'screencap', '-p', '/sdcard/screenshot.png'], check=True)
        time.sleep(0.2)  # Allow time for the screenshot to save
        subprocess.run(['adb', 'pull', '/sdcard/screenshot.png', SCREENSHOT_PATH], check=True)
        subprocess.run(['adb', 'shell', 'rm', '/sdcard/screenshot.png'], check=True)
        print(f"✔ Screenshot saved: {SCREENSHOT_PATH}")
        return SCREENSHOT_PATH
    except subprocess.CalledProcessError as e:
        print(f"❌ Error taking screenshot: {e}")
        return None

def match_templates(screenshot_path, confidence_threshold=0.6):
    """Find all matches from game templates above a confidence threshold."""
    screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
    matches = []

    for template_name in os.listdir(TEMPLATES_DIR):
        template_path = os.path.join(TEMPLATES_DIR, template_name)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

        if template is None or screenshot is None:
            continue

        # Perform template matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        locs = np.where(result >= confidence_threshold)  # Find all matches above threshold

        for pt in zip(*locs[::-1]):  # Flip (y, x) -> (x, y)
            matches.append((template_name, pt, result[pt[1], pt[0]]))  # (filename, (x, y), confidence)

    # Sort matches by confidence (highest first)
    matches.sort(key=lambda x: x[2], reverse=True)
    return matches

def tap_on_match(matched_coords):
    """Click on the matched location in ADB."""
    if matched_coords:
        x, y = matched_coords
        print(f"✔ Tapping on matched location: ({x}, {y})")
        subprocess.run(['adb', 'shell', 'input', 'tap', str(x), str(y)], check=True)
    else:
        print("❌ No valid match location found.")

# Ensure ADB is connected before starting
check_adb_connection()

# Take a new screenshot
screenshot_path = take_screenshot()

# Perform template matching
if screenshot_path:
    matches = match_templates(screenshot_path)

    if matches:
        print(f"🎯 Found {len(matches)} matches:")
        for idx, (template_name, coords, confidence) in enumerate(matches):
            print(f"   {idx+1}. {template_name} at {coords} (Confidence: {confidence:.2f})")
        
        # Tap on the best match
        best_match = matches[0]
        print(f"\n✔ Tapping on best match: {best_match[0]} at {best_match[1]}")
        tap_on_match(best_match[1])
    else:
        print("❌ No confident matches found.")
