import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import json
import pytesseract  # OCR Library

CONFIG_FILE = "config.json"
ROI_DATA_FILE = "roi_data.json"
ADB_SCREENSHOT_PATH = "/sdcard/screenshot.png"
LOCAL_SCREENSHOT_PATH = "screenshot.png"
OCR_LOG_FILE = "ocr_log.txt"

live_mode = False
roi_mode = False
roi_start = None
roi_list = []  # Store multiple ROIs
roi_counter = 1

# Load last used emulator from config
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

# Save emulator config
def save_config(device):
    config = {"last_device": device}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

# Load saved ROIs
def load_rois():
    global roi_list, roi_counter
    if os.path.exists(ROI_DATA_FILE):
        with open(ROI_DATA_FILE, "r") as f:
            roi_list = json.load(f)
        roi_counter = len(roi_list) + 1  # Continue numbering

# Save all ROIs
def save_rois():
    with open(ROI_DATA_FILE, "w") as f:
        json.dump(roi_list, f, indent=4)

# Run ADB command
def run_adb_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        messagebox.showerror("ADB Error", f"Command failed: {command}\n{e}")
        return None

# Get ADB devices
def get_connected_devices():
    output = run_adb_command(["adb", "devices"])
    return [line.split()[0] for line in output.split("\n")[1:] if "device" in line]

# Capture Screenshot
def capture_screenshot():
    device = device_var.get()
    if not device:
        messagebox.showwarning("No Device", "Select a device first.")
        return

    save_config(device)
    run_adb_command(["adb", "-s", device, "shell", "screencap", "-p", ADB_SCREENSHOT_PATH])
    run_adb_command(["adb", "-s", device, "pull", ADB_SCREENSHOT_PATH, LOCAL_SCREENSHOT_PATH])
    load_screenshot()

# Load Screenshot & Draw ROIs
def load_screenshot():
    if os.path.exists(LOCAL_SCREENSHOT_PATH):
        img = Image.open(LOCAL_SCREENSHOT_PATH)
        draw = ImageDraw.Draw(img)
        
        # Draw all saved ROIs
        for roi in roi_list:
            draw.rectangle([(roi["x1"], roi["y1"]), (roi["x2"], roi["y2"])], outline="red", width=3)

        img_tk = ImageTk.PhotoImage(img)
        screenshot_label.config(image=img_tk)
        screenshot_label.image = img_tk

# Toggle Live Mode (Disables ROI Mode)
def toggle_live_mode():
    global live_mode, roi_mode
    if roi_mode:
        roi_mode = False
        roi_button.config(text="Draw ROI: OFF")

    live_mode = not live_mode
    live_mode_btn.config(text=f"Live Mode: {'ON' if live_mode else 'OFF'}")

# Toggle ROI Mode (Disables Live Mode)
def toggle_roi_mode():
    global roi_mode, live_mode
    if live_mode:
        live_mode = False
        live_mode_btn.config(text="Live Mode: OFF")

    roi_mode = not roi_mode
    roi_button.config(text=f"Draw ROI: {'ON' if roi_mode else 'OFF'}")

# Handle Clicks (Live Mode & ROI)
def handle_click(event):
    if live_mode:
        send_adb_tap(event)
    elif roi_mode:
        start_roi(event)

# Handle ROI End Selection
def handle_release(event):
    if roi_mode:
        end_roi(event)

# Send Clicks to ADB (Live Mode)
def send_adb_tap(event):
    device = device_var.get()
    if not device:
        messagebox.showwarning("No Device", "Select a device first.")
        return

    x, y = event.x, event.y
    print(f"Live Mode: Click at {x}, {y} sent to ADB")
    run_adb_command(["adb", "-s", device, "shell", "input", "tap", str(x), str(y)])

# Record ROI Start
def start_roi(event):
    global roi_start
    roi_start = (event.x, event.y)

# Record ROI End & Save
def end_roi(event):
    global roi_mode, roi_start, roi_counter

    if roi_start:
        x1, y1 = roi_start
        x2, y2 = event.x, event.y
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        print(f"ROI #{roi_counter} Selected: ({x1}, {y1}) to ({x2}, {y2})")

        # Save ROI
        roi_list.append({"roi_id": roi_counter, "x1": x1, "y1": y1, "x2": x2, "y2": y2})
        save_rois()

        # Extract text from ROI
        extracted_text = run_ocr_on_roi(x1, y1, x2, y2)
        log_ocr_output(roi_counter, extracted_text)

        roi_counter += 1
        roi_mode = False
        roi_button.config(text="Draw ROI: OFF")
        load_screenshot()  # Reload with new ROI drawn

# Run OCR
def run_ocr_on_roi(x1, y1, x2, y2):
    img = Image.open(LOCAL_SCREENSHOT_PATH)
    roi = img.crop((x1, y1, x2, y2))
    return pytesseract.image_to_string(roi).strip()

# Log OCR Output
def log_ocr_output(roi_id, text):
    log_entry = f"ROI #{roi_id}: {text}"
    with open(OCR_LOG_FILE, "a") as f:
        f.write(log_entry + "\n")
    print(f"OCR Output Logged: {log_entry}")

# Refresh Devices
def refresh_devices():
    devices = get_connected_devices()
    device_dropdown["values"] = devices
    if config.get("last_device") in devices:
        device_var.set(config["last_device"])

# GUI Setup
root = tk.Tk()
root.title("ADB Screenshot Viewer")
root.geometry("600x700")

config = load_config()
load_rois()

# Device Selection
device_var = tk.StringVar()
device_dropdown = ttk.Combobox(root, textvariable=device_var, width=30)
device_dropdown.pack(pady=2)

# Refresh Button
refresh_devices_btn = tk.Button(root, text="Refresh Devices", command=refresh_devices)
refresh_devices_btn.pack(pady=2)

# Screenshot Display
screenshot_label = tk.Label(root)
screenshot_label.pack()

# Capture Screenshot Button
capture_btn = tk.Button(root, text="Capture Screenshot", command=capture_screenshot)
capture_btn.pack(pady=2)

# Toggle Live Mode Button
live_mode_btn = tk.Button(root, text="Live Mode: OFF", command=toggle_live_mode)
live_mode_btn.pack(pady=2)

# Draw ROI Button
roi_button = tk.Button(root, text="Draw ROI: OFF", command=toggle_roi_mode)
roi_button.pack(pady=2)

# Bind Clicks for Both Modes
screenshot_label.bind("<ButtonPress-1>", handle_click)
screenshot_label.bind("<ButtonRelease-1>", handle_release)

# Auto-load last config
refresh_devices()
load_screenshot()  # Load any saved ROIs

root.mainloop()
