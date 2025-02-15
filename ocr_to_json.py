import os
import json
import time
from PIL import Image
import pytesseract

# Update this path to the location of your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Directory containing screenshots
screenshots_dir = 'screenshots'

# Output JSON file
output_file = 'ocr_results.json'

# Initialize the JSON file
with open(output_file, 'w') as json_file:
    json.dump([], json_file)

# Counter for processed screenshots
processed_count = 0

while True:
    # List to hold filenames of screenshots to process
    screenshots_to_process = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]

    if not screenshots_to_process:
        print("No screenshots found. Exiting.")
        break

    # Process each image in the screenshots directory
    for filename in screenshots_to_process:
        image_path = os.path.join(screenshots_dir, filename)
        print(f"Processing {image_path}...")

        # Open the image file
        with Image.open(image_path) as img:
            # Perform OCR on the image
            text = pytesseract.image_to_string(img)
            print(f"OCR Result for {filename}: {text}")

            # Load existing data
            with open(output_file, 'r') as json_file:
                ocr_results = json.load(json_file)

            # Append the result to the list
            ocr_results.append({
                'filename': filename,
                'text': text.strip()
            })

            # Save the updated OCR results to the JSON file
            with open(output_file, 'w') as json_file:
                json.dump(ocr_results, json_file, indent=4)

        # Delete the screenshot after processing
        os.remove(image_path)
        print(f"Deleted {image_path}")

        # Increment the processed count
        processed_count += 1

    # Print summary
    print(f"Processed and deleted {processed_count} screenshots so far.")

    # Wait for 30 seconds before checking again
    print("Waiting for 30 seconds before checking for new screenshots...")
    time.sleep(30)

print(f"OCR results saved to {output_file}") 