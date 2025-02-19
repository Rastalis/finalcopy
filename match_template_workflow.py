import os
import cv2
import numpy as np
import subprocess
import concurrent.futures
from datetime import datetime
from skimage.metrics import structural_similarity as ssim

# 📂 Paths & Config
SCREENSHOT_PATH = "screenshots/latest_screenshot.png"
TEMPLATES_DIR = "game_templates"
OUTPUT_REPORT = "match_results.txt"

# ADB tap coordinates
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

TEMPLATE_SIZE = (50, 50)  # Standard template size for matching

# 🔍 Load Templates into Memory
def load_templates():
    templates = {}
    for category in os.listdir(TEMPLATES_DIR):
        category_path = os.path.join(TEMPLATES_DIR, category)
        if not os.path.isdir(category_path):
            continue

        for filename in os.listdir(category_path):
            template_path = os.path.join(category_path, filename)
            img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

            if img is not None:
                img = cv2.resize(img, TEMPLATE_SIZE)
                templates[template_path] = (img, category)

    print(f"✔ Loaded {len(templates)} templates, resized for matching.")
    return templates

# 📸 Capture Screenshot
def take_screenshot():
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    print("📸 Taking new screenshot...")
    subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screenshot.png"], check=True)
    subprocess.run(["adb", "pull", "/sdcard/screenshot.png", SCREENSHOT_PATH], check=True)
    subprocess.run(["adb", "shell", "rm", "/sdcard/screenshot.png"], check=True)

    print(f"✔ Screenshot saved: {SCREENSHOT_PATH}")

# 📂 Load Screenshot
def load_screenshot():
    if not os.path.exists(SCREENSHOT_PATH):
        take_screenshot()

    screenshot = cv2.imread(SCREENSHOT_PATH, cv2.IMREAD_GRAYSCALE)
    if screenshot is None:
        print("❌ Failed to load screenshot!")
        return None

    print(f"✔ Screenshot loaded: {screenshot.shape}")
    return screenshot

# 🔍 Feature Matching using SIFT & SSIM
def match_template(template, screenshot, template_name):
    sift = cv2.SIFT_create(nfeatures=2000)  # More keypoints
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(screenshot, None)

    if des1 is None or des2 is None:
        return None  # Skip if features cannot be detected

    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(des1, des2)

    match_score = len(matches)

    if match_score > 10:  # Lowered threshold
        return (template_name, match_score)

    # Secondary check using SSIM
    resized_template = cv2.resize(template, screenshot.shape[::-1])
    ssim_score = ssim(resized_template, screenshot)

    if ssim_score > 0.85:  # Adjust SSIM threshold
        return (template_name, int(ssim_score * 100))

    return None

# ⚡ Parallel Template Matching
def match_templates_parallel(screenshot, templates):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_template = {
            executor.submit(match_template, template, screenshot, name): (name, category)
            for name, (template, category) in templates.items()
        }

        for future in concurrent.futures.as_completed(future_to_template):
            result = future.result()
            if result:
                results.append(result)

    results = sorted(results, key=lambda x: x[1], reverse=True)

    # 🔍 Debug: Print top 5 matches
    print("\n🔍 TOP 5 TEMPLATE MATCHES:")
    for i, (template_name, score) in enumerate(results[:5]):
        print(f"  {i+1}. {template_name} - Score: {score}")

    return results

# 📊 Save Matching Results
def save_report(matched_results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_matches = len(matched_results)

    highest_match = max(matched_results, key=lambda x: x[1], default=("None", 0))
    lowest_match = min(matched_results, key=lambda x: x[1], default=("None", 0))

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as report:
        report.write(f"📊 Template Matching Report ({timestamp})\n")
        report.write("=" * 60 + "\n")
        for template, score in matched_results:
            report.write(f"{template}: Score {score}\n")

        report.write("\n📊 Summary\n")
        report.write("=" * 60 + "\n")
        report.write(f"🔹 Total Template Matches Found: {total_matches}\n")
        report.write(f"🔹 Highest Match: {highest_match[0]} (Score: {highest_match[1]})\n")
        report.write(f"🔹 Lowest Match: {lowest_match[0]} (Score: {lowest_match[1]})\n")

    print(f"📄 Report saved: {OUTPUT_REPORT}")
    print("\n📊 SUMMARY 📊")
    print(f"🔹 Total Template Matches Found: {total_matches}")
    print(f"🔹 Best Match: {highest_match[0]} (Score: {highest_match[1]})")
    print(f"🔹 Worst Match: {lowest_match[0]} (Score: {lowest_match[1]})")

# 🚀 Main Execution
def main():
    print("🔍 Loading templates into memory...")
    templates = load_templates()

    print("📸 Checking for screenshot...")
    screenshot = load_screenshot()

    if screenshot is None:
        print("❌ Screenshot could not be loaded. Exiting.")
        return

    print("⚡ Performing parallel template matching...")
    matched_results = match_templates_parallel(screenshot, templates)

    print("📊 Saving report...")
    save_report(matched_results)

    print("✅ Optimized template matching completed!")

if __name__ == "__main__":
    main()
