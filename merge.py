import os
import json
import time
import re
from datetime import datetime
from PIL import Image
import pytesseract

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Directories and files
SCREENSHOTS_DIR = 'screenshots'
OUTPUT_FILE = 'ocr_results.json'
NAVIGATION_POINTS_FILE = 'navigation_points.json'

# Total number of tiles in the grid
TOTAL_TILES = 511 * 1023

# Ensure JSON file exists
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'w') as f:
        json.dump([], f)

# Track the starting time
start_time = time.time()

def load_existing_results():
    """Load existing OCR results from the JSON file."""
    try:
        with open(OUTPUT_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def load_navigation_points():
    """Load navigation points as (K, X, Y) tuples from the JSON file."""
    try:
        with open(NAVIGATION_POINTS_FILE, 'r') as f:
            navigation_data = json.load(f)

        # Ensure the JSON contains a "points" key
        if "points" in navigation_data and isinstance(navigation_data["points"], list):
            return {(point[0], point[1], point[2]) for point in navigation_data["points"] if len(point) == 3}

        print("Warning: 'points' key missing or incorrectly formatted in navigation_points.json.")
        return set()
    
    except (FileNotFoundError, json.JSONDecodeError):
        print("Warning: Navigation points file not found or invalid.")
        return set()

def extract_timestamp(filename):
    """Extract the timestamp from the filename (assuming format: screenshot_YYYYMMDD_HHMMSS.png)."""
    parts = filename.split('_')
    if len(parts) > 2:
        timestamp_str = parts[1] + '_' + parts[2].split('.')[0]
    else:
        timestamp_str = parts[1]  # Only date is present
    try:
        return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
    except ValueError:
        return datetime.strptime(timestamp_str, "%Y%m%d")

def process_images():
    """Process all images in the screenshots directory."""
    if not os.path.exists(SCREENSHOTS_DIR):
        print(f"Error: Directory '{SCREENSHOTS_DIR}' not found.")
        return

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

            os.remove(image_path)  # Delete the screenshot after processing
            print(f"Deleted {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(ocr_results, f, indent=4)

    print(f"Processed {len(screenshots)} images.")

def analyze_ocr_data():
    """Analyze OCR results and generate a report."""
    ocr_data = load_existing_results()
    
    if not ocr_data:
        print("No data found in the JSON file.")
        return

    first_entry_timestamp = extract_timestamp(ocr_data[0]['filename'])
    elapsed_time = datetime.now() - first_entry_timestamp

    kxy_pattern = re.compile(r'K:(\d+)\s*X:(\d+)\s*Y:(\d+)')

    total_kxy_entries = 0
    total_non_kxy_entries = 0
    unique_kxy_entries = set()

    for entry in ocr_data:
        text = entry.get('text', '')
        match = kxy_pattern.search(text)
        if match:
            total_kxy_entries += 1
            k, x, y = map(int, match.groups())  # Extract (K, X, Y)
            unique_kxy_entries.add((k, x, y))  # Store as tuple
        else:
            total_non_kxy_entries += 1

    total_entries = len(ocr_data)

    # Load navigation points (K, X, Y)
    navigation_points = load_navigation_points()

    # Count navigation points that have been visited
    used_navigation_points = unique_kxy_entries.intersection(navigation_points)
    used_navigation_count = len(used_navigation_points)
    navigation_coverage_percentage = (used_navigation_count / len(navigation_points)) * 100 if navigation_points else 0

    # Calculate estimated time to completion
    time_elapsed = time.time() - start_time  # Time elapsed in seconds
    unique_kxy_count = len(unique_kxy_entries)
    remaining_kxy = TOTAL_TILES - unique_kxy_count

    if time_elapsed > 0 and unique_kxy_count > 0:
        rate_per_second = unique_kxy_count / time_elapsed
        if rate_per_second > 0:
            estimated_seconds_remaining = remaining_kxy / rate_per_second
            estimated_completion_time = time.strftime('%H:%M:%S', time.gmtime(estimated_seconds_remaining))
        else:
            estimated_completion_time = "∞ (No progress detected)"
    else:
        estimated_completion_time = "Calculating..."

    report = {
        "total_kxy_entries": total_kxy_entries,
        "total_non_kxy_entries": total_non_kxy_entries,
        "unique_kxy_entries_count": unique_kxy_count,
        "percentage_unique_kxy_vs_grid": (unique_kxy_count / TOTAL_TILES) * 100,
        "used_navigation_points": used_navigation_count,
        "navigation_coverage_percentage": navigation_coverage_percentage,
        "elapsed_time": str(elapsed_time),
        "estimated_completion_time": estimated_completion_time
    }

    print("\nKXY Data Analysis Report")
    print("========================")
    print(f"Total entries with KXY data: {total_kxy_entries} ({(total_kxy_entries / total_entries) * 100:.2f}%)")
    print(f"Total entries without KXY data: {total_non_kxy_entries} ({(total_non_kxy_entries / total_entries) * 100:.2f}%)")
    print(f"Unique KXY entries count: {unique_kxy_count}")
    print(f"Percentage of unique KXY entries vs. total grid: {report['percentage_unique_kxy_vs_grid']:.2f}%")
    print(f"Navigation points used: {used_navigation_count} / {len(navigation_points)}")
    print(f"Navigation coverage: {navigation_coverage_percentage:.2f}%")
    print(f"Elapsed time since first entry: {elapsed_time}")
    print(f"Estimated time to completion: {estimated_completion_time}\n")

# Continuous Monitoring Loop
print("Monitoring for new screenshots and analyzing data...")
while True:
    process_images()
    analyze_ocr_data()
    print("\nWaiting for 30 seconds before the next cycle...\n")
    time.sleep(30)  # Wait before next run
