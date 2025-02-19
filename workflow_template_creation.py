import os
import subprocess
import time
import logging
from datetime import datetime
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import cv2
import numpy as np
import imagehash
from skimage.metrics import structural_similarity as ssim

# 📂 Paths & Config
LOG_FILE = "scan_summary.log"
SCREENSHOT_DIR = "screenshots"
TEMPLATE_DIR = "game_templates"
FAILED_TILES_DIR = "failed_tiles"
TEMPLATE_DIRS = ["resources", "enemies", "terrain", "darknest", "unknown"]

# 🛠️ Logging Setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# 📌 Tile Processing Parameters
CROP_SIZE = 50
SIMILARITY_THRESHOLD = 0.90
BLANK_THRESHOLD = 0.98
HASH_THRESHOLD = 6
ORB_MATCH_THRESHOLD = 30
TEMPLATE_SIZE = (50, 50)

# 🔥 Performance Tracking
TILES_SCANNED = 0
TEMPLATES_CREATED = 0
FAILED_TILES = 0

# 📂 Ensure Directories Exist
for folder in TEMPLATE_DIRS:
    os.makedirs(f"{TEMPLATE_DIR}/{folder}", exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(FAILED_TILES_DIR, exist_ok=True)

# 🗺️ ADB tap coordinates
coordinates = [
    (99, 451),
    (332, 451),
    (568, 451),
    (802, 451),
    (1031, 451),
    (1262, 451),
    (1479, 451),
    (99, 893),
    (332, 893),
    (568, 893),
    (802, 893),
    (1031, 893),
    (1262, 893),
    (1470, 889),
    (15, 850),
    (215, 850),
    (450, 850),
    (684, 850),
    (916, 850),
    (1145, 850),
    (1377, 850),
    (99, 451),
    (332, 451),
    (568, 451),
    (802, 451),
    (1031, 451),
    (1262, 451),
    (1479, 451),
    (99, 893),
    (332, 893),
    (568, 893),
    (802, 893),
    (1031, 893),
    (1262, 893),
    (1470, 889),
    (15, 850),
    (215, 850),
    (450, 850),
    (684, 850),
    (916, 850),
    (1145, 850),
    (1377, 850),
    (99, 795),
    (332, 795),
    (568, 795),
    (802, 795),
    (1031, 795),
    (1262, 795),
    (1470, 795),
    (215, 734),
    (450, 734),
    (684, 734),
    (916, 734),
    (1145, 734),
    (1377, 734),
    (1581, 734),
    (99, 678),
    (332, 678),
    (568, 678),
    (802, 678),
    (1031, 678),
    (1262, 678),
    (1479, 678),
    (215, 620),
    (450, 620),
    (684, 620),
    (916, 620),
    (1145, 620),
    (1377, 620),
    (1581, 620),
    (99, 562),
    (332, 562),
    (568, 562),
    (802, 562),
    (1031, 562),
    (1262, 562),
    (1479, 562),
    (8, 505),
    (215, 505),
    (450, 505),
    (684, 505),
    (916, 505),
    (1145, 505),
    (1377, 505),
    (1581, 505),
    (8, 394),
    (215, 394),
    (450, 394),
    (684, 394),
    (916, 394),
    (1145, 394),
    (1377, 394),
    (1581, 394),
    (99, 338),
    (332, 338),
    (568, 338),
    (802, 338),
    (1031, 338),
    (1262, 338),
    (1479, 338),
    (8, 281),
    (215, 281),
    (450, 281),
    (684, 281),
    (916, 281),
    (1145, 281),
    (1377, 281),
    (1581, 265),
    (99, 225),
    (332, 225),
    (568, 225),
    (802, 225),
    (1031, 225),
    (1262, 225),
    (1479, 225),
    (8, 168),
    (215, 168),
    (450, 168),
    (684, 168),
    (916, 168),
    (1145, 168),
    (1377, 168),
    (1581, 168),
    (99, 112),
    (332, 112),
    (568, 112),
    (799, 89),
    (1012, 89),
    (1262, 112),
    (1442, 101),
    (8, 61),
    (215, 61),
    (373, 61),
    (1392, 61)
    # Add more coordinates as needed
]

# 📌 Track saved templates
SAVED_TEMPLATES = set()

# 🔍 **Utility Functions**
def take_screenshot():
    """Captures a screenshot via ADB."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"{SCREENSHOT_DIR}/screenshot_{timestamp}.png"

    try:
        subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screenshot.png"], check=True)
        time.sleep(0.2)
        subprocess.run(["adb", "pull", "/sdcard/screenshot.png", screenshot_path], check=True)
        subprocess.run(["adb", "shell", "rm", "/sdcard/screenshot.png"], check=True)

        print(f"✔ Screenshot saved: {screenshot_path}")
        return screenshot_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Error taking screenshot: {e}")
        return None


def crop_image(img, x, y):
    """Returns a cropped region around the given coordinate."""
    left = max(x - CROP_SIZE // 2, 0)
    upper = max(y - CROP_SIZE // 2, 0)
    right = min(x + CROP_SIZE // 2, img.width)
    lower = min(y + CROP_SIZE // 2, img.height)
    return img.crop((left, upper, right, lower))


def preprocess_image_for_ocr(image):
    """Enhances image for better OCR performance."""
    gray = ImageOps.grayscale(image)
    contrast = ImageEnhance.Contrast(gray).enhance(2.0)
    sharp = ImageEnhance.Sharpness(contrast).enhance(2.0)
    return sharp


def extract_text_from_image(image):
    """Uses OCR to extract text from an image after preprocessing."""
    processed_img = preprocess_image_for_ocr(image)
    text = pytesseract.image_to_string(processed_img).strip()
    return text


def classify_tile_by_text(text):
    """Classifies the tile based on detected text."""
    if any(word in text.lower() for word in ["wood", "stone", "gold", "food", "vein", "ruins"]):
        return "resources"
    if any(word in text.lower() for word in ["darknest", "min.", "2-player"]):
        return "darknest"
    if any(word in text.lower() for word in ["guild", "profile", "troops killed"]):
        return "enemies"
    if any(word in text.lower() for word in ["grass", "forest", "mountain", "beach", "lava"]):
        return "terrain"
    return "unknown"


def save_template(image, category, x, y):
    """Saves a template image with a unique filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{category}_X{x}_Y{y}_{timestamp}.png"
    save_path = f"{TEMPLATE_DIR}/{category}/{filename}"

    if save_path not in SAVED_TEMPLATES:
        image.save(save_path)
        SAVED_TEMPLATES.add(save_path)
        print(f"✔ Saved: {save_path} (Category: {category})")
        return True
    return False


def process_all_templates(screenshot_path):
    """Scans all tiles, labels them, and prevents overwriting templates."""
    global TILES_SCANNED, TEMPLATES_CREATED, FAILED_TILES

    try:
        with Image.open(screenshot_path) as img:
            for (x, y) in coordinates:
                TILES_SCANNED += 1
                cropped_img = crop_image(img, x, y)

                text = extract_text_from_image(cropped_img)
                category = classify_tile_by_text(text)

                if save_template(cropped_img, category, x, y):
                    TEMPLATES_CREATED += 1
                else:
                    FAILED_TILES += 1

        print(f"\n📊 SUMMARY: {TEMPLATES_CREATED} new templates created, {FAILED_TILES} duplicates skipped.")
    except Exception as e:
        logging.error(f"❌ Error: {e}")


# **📌 Run Process**
screenshot_path = take_screenshot()

if screenshot_path:
    process_all_templates(screenshot_path)

print("✅ Template generation complete!")
