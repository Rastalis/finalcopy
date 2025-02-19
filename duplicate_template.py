import os
import cv2
import numpy as np

# Folder containing template images
TEMPLATES_DIR = "game_templates"
DUPLICATE_REPORT = "duplicate_report.txt"
SIMILARITY_THRESHOLD = 0.98  # Adjust threshold (1.0 = identical)

def load_images():
    """Load all images from the folder."""
    images = {}
    for filename in os.listdir(TEMPLATES_DIR):
        path = os.path.join(TEMPLATES_DIR, filename)
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale
        if img is not None:
            images[filename] = img
    return images

def compare_images(img1, img2):
    """Compare two images using histogram similarity."""
    hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])

    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()

    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)  # Compare histograms
    return similarity

def find_duplicates(images):
    """Find duplicate images based on histogram similarity."""
    duplicates = []
    checked = set()

    keys = list(images.keys())

    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            img1, img2 = keys[i], keys[j]

            if (img1, img2) in checked or (img2, img1) in checked:
                continue  # Skip already checked pairs

            similarity = compare_images(images[img1], images[img2])

            if similarity >= SIMILARITY_THRESHOLD:
                duplicates.append((img1, img2, similarity))
            
            checked.add((img1, img2))

    return duplicates

def delete_duplicates(duplicates):
    """Delete duplicate images and keep the first occurrence."""
    deleted_count = 0
    for img1, img2, score in duplicates:
        duplicate_path = os.path.join(TEMPLATES_DIR, img2)
        
        if os.path.exists(duplicate_path):  # ✅ Check if file exists
            os.remove(duplicate_path)
            deleted_count += 1
            print(f"🗑️ Deleted duplicate: {img2} (Similarity: {score:.2f})")
        else:
            print(f"⚠️ Warning: {img2} not found, skipping...")  # ✅ Log missing files

    print(f"✔ Deleted {deleted_count} duplicate images.")
    return deleted_count


def re_label_images():
    """Re-label remaining images in numerical order."""
    images = sorted(os.listdir(TEMPLATES_DIR))
    for idx, filename in enumerate(images, start=1):
        new_name = f"template_{idx:03d}.png"
        old_path = os.path.join(TEMPLATES_DIR, filename)
        new_path = os.path.join(TEMPLATES_DIR, new_name)

        os.rename(old_path, new_path)
        print(f"Renamed {filename} → {new_name}")

def save_report(duplicates):
    """Save duplicate report to file."""
    with open(DUPLICATE_REPORT, "w") as f:
        f.write("Duplicate Image Report\n")
        f.write("======================\n")
        if not duplicates:
            f.write("No duplicates found.\n")
        else:
            for img1, img2, score in duplicates:
                f.write(f"{img1} == {img2} (Similarity: {score:.2f})\n")

    print(f"✔ Duplicate report saved: {DUPLICATE_REPORT}")

# Run duplicate detection, deletion, and renaming
images = load_images()
duplicates = find_duplicates(images)

if duplicates:
    save_report(duplicates)
    delete_duplicates(duplicates)
    re_label_images()
else:
    print("✅ No duplicate images found.")
