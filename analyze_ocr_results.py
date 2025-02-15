import json
import re
import time
from datetime import datetime

# Total number of tiles in the grid
total_tiles = 511 * 1023

def extract_timestamp(filename):
    # Extract the timestamp from the filename
    # Assuming the format is 'screenshot_YYYYMMDD_HHMMSS.png'
    # Adjusting to handle cases where time might be missing
    parts = filename.split('_')
    if len(parts) > 2:
        timestamp_str = parts[1] + '_' + parts[2].split('.')[0]
    else:
        timestamp_str = parts[1]  # Only date is present
    try:
        return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
    except ValueError:
        return datetime.strptime(timestamp_str, "%Y%m%d")

while True:
    # Load the OCR results from the JSON file
    with open('ocr_results.json', 'r') as file:
        ocr_data = json.load(file)

    if not ocr_data:
        print("No data found in the JSON file. Exiting.")
        break

    # Extract the timestamp from the first entry
    first_entry_timestamp = extract_timestamp(ocr_data[0]['filename'])
    current_time = datetime.now()
    elapsed_time = current_time - first_entry_timestamp

    # Regular expression to find KXY data
    kxy_pattern = re.compile(r'K:(\d+)\s*X:(\d+)\s*Y:(\d+)')

    # Initialize counters and sets
    total_kxy_entries = 0
    total_non_kxy_entries = 0
    unique_kxy_entries = set()

    # Process each entry in the OCR data
    for entry in ocr_data:
        text = entry.get('text', '')
        match = kxy_pattern.search(text)
        if match:
            total_kxy_entries += 1
            kxy_data = match.group(0)
            unique_kxy_entries.add(kxy_data)
        else:
            total_non_kxy_entries += 1

    # Calculate total entries
    total_entries = len(ocr_data)

    # Generate the report
    report = {
        "total_kxy_entries": total_kxy_entries,
        "total_non_kxy_entries": total_non_kxy_entries,
        "unique_kxy_entries_count": len(unique_kxy_entries),
    }

    # Print the report
    print("KXY Data Analysis Report")
    print("========================")
    print(f"Total entries with KXY data: {report['total_kxy_entries']} ({(report['total_kxy_entries'] / total_entries) * 100:.2f}%)")
    print(f"Total entries without KXY data: {report['total_non_kxy_entries']} ({(report['total_non_kxy_entries'] / total_entries) * 100:.2f}%)")
    print(f"Unique KXY entries count: {report['unique_kxy_entries_count']}")
    print(f"Percentage of unique KXY entries compared to total grid tiles: {(report['unique_kxy_entries_count'] / total_tiles) * 100:.2f}%")
    print(f"Elapsed time since first entry: {elapsed_time}")

    # Wait for 65 seconds before running again
    print("\nWaiting for 30 seconds before the next analysis...\n")
    time.sleep(30) 