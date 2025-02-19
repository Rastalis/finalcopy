import os
import json
import time
from PIL import Image
import pytesseract

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Directories and files
SCREENSHOTS_DIR = 'screenshots'
OUTPUT_FILE = 'ocr_results.json'

# Ensure JSON file exists
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'w') as f:
        json.dump([], f)

def load_existing_results():
    """Load existing OCR results from the JSON file."""
    try:
        with open(OUTPUT_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def process_images():
    """Process all images in the screenshots directory."""
    if not os.path.exists(SCREENSHOTS_DIR):
        print(f"Error: Directory '{SCREENSHOTS_DIR}' not found.")
        return
    
    # Get all images in the directory
    screenshots = [f for f in os.listdir(SCREENSHOTS_DIR) if f.endswith('.png')]
    if not screenshots:
        print("No new screenshots found.")
        return
    
    ocr_results = load_existing_results()

    for filename in screenshots:
        image_path = os.path.join(SCREENSHOTS_DIR, filename)
        print(f"Processing {filename}...")

        try:
            with Image.open(image_path) as img:
                text = pytesseract.image_to_string(img).strip()

            ocr_results.append({'filename': filename, 'text': text})

            # Delete the screenshot after processing
            os.remove(image_path)
            print(f"Deleted {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Save results in bulk
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(ocr_results, f, indent=4)
    
    print(f"Processed {len(screenshots)} images.")

# Continuous monitoring loop
print("Monitoring for new screenshots...")
while True:
    process_images()
    time.sleep(30)  # Wait before checking again
