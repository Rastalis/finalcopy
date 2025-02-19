import os
import imagehash
from PIL import Image
from collections import defaultdict

# Configuration
TEMPLATE_DIR = "game_templates"  # Root folder for templates
SIMILARITY_THRESHOLD = 5  # Lower = Stricter match, usually 0-10 is a good range
REPORT_PATH = "duplicate_templates_report.txt"  # Report file

def get_image_hashes():
    """Scans all images in template folders and returns a dictionary of {filename: hash}."""
    hashes = {}
    
    for category in os.listdir(TEMPLATE_DIR):
        category_path = os.path.join(TEMPLATE_DIR, category)

        if not os.path.isdir(category_path):
            continue  # Skip non-folder items

        for filename in os.listdir(category_path):
            file_path = os.path.join(category_path, filename)
            
            try:
                with Image.open(file_path) as img:
                    img_hash = imagehash.phash(img)  # Compute perceptual hash
                    hashes[file_path] = img_hash
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")

    return hashes

def find_and_delete_duplicates(hashes):
    """Finds and deletes duplicate images, keeping only one unique version."""
    similar_images = defaultdict(list)
    checked_pairs = set()
    deleted_files = []

    file_list = list(hashes.keys())

    for i, file1 in enumerate(file_list):
        for j in range(i + 1, len(file_list)):  # Avoid redundant comparisons
            file2 = file_list[j]
            if (file1, file2) in checked_pairs or (file2, file1) in checked_pairs:
                continue  # Skip already checked pairs
            
            hash_diff = hashes[file1] - hashes[file2]

            if hash_diff <= SIMILARITY_THRESHOLD:
                similar_images[file1].append(file2)
                
                # Check if the file exists before deleting
                if os.path.exists(file2):
                    os.remove(file2)  
                    deleted_files.append(file2)
                    print(f"🗑 Deleted duplicate: {file2}")
                else:
                    print(f"⚠️ Skipped deletion (file not found): {file2}")

            checked_pairs.add((file1, file2))

    return similar_images, deleted_files

def save_report(similar_images, deleted_files):
    """Saves a report of similar and deleted images to a file with UTF-8 encoding."""
    with open(REPORT_PATH, "w", encoding="utf-8") as report:  # ✅ Force UTF-8 Encoding
        report.write("📝 Similar Image Report\n")
        report.write("="*40 + "\n\n")

        for main_img, duplicates in similar_images.items():
            report.write(f"{main_img} is similar to:\n")
            for dup in duplicates:
                status = "DELETED" if dup in deleted_files else "SKIPPED"
                report.write(f"    - {dup} ({status})\n")
            report.write("\n")

        report.write("="*40 + "\n")
        report.write(f"Total Deleted: {len(deleted_files)}\n")

    print(f"✔ Report saved: {REPORT_PATH}")

def main():
    print("🔍 Scanning template folders for similar images...")
    hashes = get_image_hashes()
    
    print("📝 Comparing templates and deleting duplicates...")
    similar_images, deleted_files = find_and_delete_duplicates(hashes)

    print("📊 Saving report...")
    save_report(similar_images, deleted_files)

    print("✅ Completed! Check duplicate_templates_report.txt.")

if __name__ == "__main__":
    main()
